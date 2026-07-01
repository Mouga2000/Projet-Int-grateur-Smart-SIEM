#!/usr/bin/env python3
"""
Ingère le dataset CLUE-LDS dans Elasticsearch pour l'entraînement UEBA.

Deux modes :
  - fast (défaut) : écriture directe dans ES via bulk API (10000+ evt/s)
  - api           : via l'API SIEM (lent, ~100 evt/s, mais déclenche la normalisation)

Le mode "fast" est recommandé pour ingérer les 50M événements.
Le mode "api" est utile pour tester le pipeline complet avec un petit échantillon.

Utilisation :
    # Fast : ingestion massive directe ES (recommandé)
    python scripts/ingest_clue_lds.py clue.json --fast

    # API : via le SIEM (pour test, max 1000 événements)
    python scripts/ingest_clue_lds.py clue.json --api --max 1000

Options :
    --max N         Nombre max d'événements (défaut: illimité)
    --batch N       Taille du lot (défaut: 2000 pour fast, 500 pour api)
    --resume        Reprendre depuis le dernier checkpoint
    --no-checkpoint Désactiver la sauvegarde de progression
"""

import json
import os
import sys
import time
from typing import List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CHECKPOINT_FILE = "clue_checkpoint.txt"
DEFAULT_API_URL = "http://localhost:8000/api/v1/logs/ingest"
ES_INDEX = "logs-clue"  # Index dédié pour les données CLUE


def get_es_client():
    """Retourne un client Elasticsearch asynchrone."""
    from elasticsearch import helpers
    from app.core.elasticsearch import ElasticsearchClient
    return ElasticsearchClient(), helpers


def map_event(raw: dict) -> dict:
    """
    Mappe un événement CLUE-LDS vers le format de document Elasticsearch.

    Contrairement au mode API, on écrit directement dans un format que
    le service UEBA peut lire (pas de normalisation SIEM).
    """
    uid = raw.get("uid", "unknown")
    ts = raw.get("time")

    # Construction du document au format attendu par extract_features()
    doc = {
        "timestamp":    ts,
        "source_ip":    raw.get("ip", "0.0.0.0"),
        "host":         uid,
        "log_type":     raw.get("type", "application"),
        "severity":     "info",
        "raw_message":  json.dumps(raw, default=str),
        "tags":         ["clue", raw.get("type", "unknown")],
        "decoded": {
            "user": uid,  # ← essentiel pour le groupement UEBA
        },
        "raw_data": {
            "uid":         uid,
            "uid_type":    raw.get("uidType"),
            "role":        raw.get("role"),
            "location":    raw.get("location"),
            "is_local_ip": raw.get("isLocalIP", False),
            "params":      raw.get("params", {}),
        },
    }

    # Ajouter le pays comme tag pour analyse géographique
    loc = raw.get("location", {})
    if isinstance(loc, dict) and loc.get("countryCode"):
        doc["tags"].append(f"country:{loc['countryCode']}")

    return doc


# ===========================================================================
# MODE FAST — ES Bulk Direct
# ===========================================================================


def ingest_fast(
    filepath: str,
    max_events: Optional[int] = None,
    batch_size: int = 2000,
    use_checkpoint: bool = True,
):
    """
    Ingestion massive via Elasticsearch helpers.asyanc_bulk.

    ~10 000 événements/seconde → 50M en ~1h30.
    """
    import asyncio
    from elasticsearch import AsyncElasticsearch

    async def _run():
        # Connexion ES
        es = AsyncElasticsearch(["http://localhost:9200"])

        # Créer l'index avec mapping adapté si inexistant
        if not await es.indices.exists(index=ES_INDEX):
            await es.indices.create(index=ES_INDEX, body={
                "settings": {"number_of_shards": 3, "number_of_replicas": 0},
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "date"},
                        "source_ip": {"type": "ip"},
                        "host":      {"type": "keyword"},
                        "log_type":  {"type": "keyword"},
                        "severity":  {"type": "keyword"},
                        "tags":      {"type": "keyword"},
                        "decoded": {
                            "properties": {
                                "user": {"type": "keyword"},
                            }
                        },
                    }
                },
            })

        if not os.path.exists(filepath):
            print(f"Fichier introuvable : {filepath}")
            return

        file_size = os.path.getsize(filepath)
        print(f"Fichier : {filepath} ({file_size/1e9:.1f} Go)")
        print(f"Index   : {ES_INDEX}")
        print(f"Mode    : ES bulk direct")
        print(f"Lot     : {batch_size} evts/batch")
        print(f"---")

        # Reprise ?
        start_line = 0
        if use_checkpoint and os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE) as cf:
                saved = cf.read().strip()
                if saved:
                    start_line = int(saved)
                    print(f"Checkpoint trouve : reprise a la ligne {start_line}")

        total, errors, line_num = 0, 0, 0
        actions, batch_count = [], 0
        start = time.time()

        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if line_num <= start_line:
                    continue

                line = line.strip()
                if not line:
                    continue

                try:
                    raw = json.loads(line)
                except json.JSONDecodeError:
                    continue

                doc = map_event(raw)
                actions.append({"_index": ES_INDEX, "_source": doc})
                batch_count += 1

                if batch_count >= batch_size:
                    success, errs = await _bulk_send(es, actions)
                    total += success
                    errors += errs
                    actions, batch_count = [], 0

                    if use_checkpoint:
                        with open(CHECKPOINT_FILE, "w") as cf:
                            cf.write(str(line_num))

                    if max_events and total >= max_events:
                        break

                    _progress(total, errors, start, line_num)

        # Dernier lot
        if actions:
            success, errs = await _bulk_send(es, actions)
            total += success
            errors += errs

        if use_checkpoint and os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)

        elapsed = time.time() - start
        rate = total / elapsed if elapsed > 0 else 0
        print(f"\n---")
        print(f"Termine : {total} evenements indexes en {elapsed:.1f}s")
        print(f"Debit   : {rate:.0f} evt/s")
        print(f"Erreurs : {errors}")

        await es.close()

    asyncio.run(_run())


async def _bulk_send(es, actions: list) -> tuple:
    """Envoie un lot à ES et retourne (success, errors)."""
    from elasticsearch import helpers

    try:
        success, errors = await helpers.async_bulk(
            es, actions, raise_on_error=False, refresh=False
        )
        return success, len(errors) if isinstance(errors, list) else 0
    except Exception as e:
        print(f"\n  Erreur bulk: {e}")
        return 0, len(actions)


_last_progress = 0


def _progress(total: int, errors: int, start: float, line: int):
    """Affiche la progression (max 1x/seconde)."""
    global _last_progress
    now = time.time()
    if now - _last_progress < 1:
        return
    _last_progress = now
    elapsed = now - start
    rate = total / elapsed if elapsed > 0 else 0
    print(f"  {total} evts | {rate:.0f} evt/s | ligne {line} | erreurs {errors}", flush=True)


# ===========================================================================
# MODE API — Via le SIEM (lent mais avec normalisation)
# ===========================================================================


def ingest_via_api(
    filepath: str,
    max_events: Optional[int] = None,
    batch_size: int = 500,
    api_url: str = DEFAULT_API_URL,
    use_checkpoint: bool = True,
):
    """
    Ingestion via l'API SIEM. Déclenche la normalisation et la corrélation.
    Utile pour tester le pipeline complet avec un petit echantillon.
    """
    import httpx

    if not os.path.exists(filepath):
        print(f"Fichier introuvable : {filepath}")
        return

    print(f"Fichier : {filepath}")
    print(f"API     : {api_url}")
    print(f"Mode    : API SIEM (lent)")
    print(f"---")

    total, batch = 0, []
    start = time.time()

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue

            doc = map_event(raw)
            batch.append(doc)

            if len(batch) >= batch_size:
                total += _send_batch_api(batch, api_url)
                batch = []

            if max_events and total >= max_events:
                break

    if batch:
        total += _send_batch_api(batch, api_url)

    elapsed = time.time() - start
    rate = total / elapsed if elapsed > 0 else 0
    print(f"---")
    print(f"Termine : {total} evenements en {elapsed:.1f}s ({rate:.0f} evt/s)")


def _send_batch_api(batch: list, api_url: str) -> int:
    """Envoie un lot à l'API REST du SIEM."""
    import httpx

    success = 0
    for doc in batch:
        try:
            resp = httpx.post(api_url, json=doc, timeout=10)
            if resp.status_code == 200:
                success += 1
            else:
                print(f"  Erreur {resp.status_code}: {resp.text[:80]}")
        except httpx.ConnectError:
            print(f"  Serveur {api_url} injoignable")
            return success
        except Exception as e:
            print(f"  Exception: {e}")
    print(f"  > {success}/{len(batch)}", flush=True)
    return success


# ===========================================================================
# POINT D'ENTRÉE
# ===========================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Ingestion du dataset CLUE-LDS pour l'UEBA"
    )
    parser.add_argument("filepath", nargs="?", default="clue.json",
                        help="Chemin vers clue.json")
    parser.add_argument("--fast", action="store_true", default=True,
                        help="Mode ES bulk direct (rapide, defaut)")
    parser.add_argument("--api", action="store_true",
                        help="Mode API SIEM (lent, pour test)")
    parser.add_argument("--max", type=int, default=None,
                        help="Nombre max d'evenements")
    parser.add_argument("--batch", type=int, default=None,
                        help="Taille du lot")
    parser.add_argument("--resume", action="store_true",
                        help="Reprendre depuis le checkpoint")
    parser.add_argument("--no-checkpoint", action="store_true",
                        help="Desactiver le checkpoint")

    args = parser.parse_args()

    use_fast = not args.api  # fast par défaut

    if args.api:
        ingest_via_api(
            filepath=args.filepath,
            max_events=args.max,
            batch_size=args.batch or 500,
            use_checkpoint=not args.no_checkpoint,
        )
    else:
        ingest_fast(
            filepath=args.filepath,
            max_events=args.max,
            batch_size=args.batch or 2000,
            use_checkpoint=not args.no_checkpoint,
        )
