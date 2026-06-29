#!/usr/bin/env python3
"""
Entraîne le modèle UEBA (Isolation Forest) sur les données CLUE-LDS.

Deux modes :
  --file clue.json   Lecture directe du fichier (rapide, recommandé)
  --index logs-clue  Lecture depuis Elasticsearch (si déjà ingéré)

Étapes :
  1. Charge les événements (fichier ou ES)
  2. Groupe par utilisateur
  3. Extrait les features (8 dimensions)
  4. Entraîne Isolation Forest
  5. Sauvegarde le modèle dans models/ueba/isolation_forest.joblib
  6. Met à jour les profils dans profils_ueba (PostgreSQL)

Utilisation :
    python scripts/train_ueba.py --file docs/clue.json
    python scripts/train_ueba.py --file docs/clue.json --sample 500000
    python scripts/train_ueba.py --index logs-clue
"""

import argparse
import asyncio
import json
import sys
import os
import time
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services import ueba as ueba_service
from app.core.database import async_session_factory


# ===========================================================================
# MODE FICHIER
# ===========================================================================


def load_from_file(filepath: str, sample: int = None):
    """
    Lit clue.json ligne par ligne et groupe par utilisateur.
    Beaucoup plus rapide que de passer par ES.
    """
    if not os.path.exists(filepath):
        print(f"Fichier introuvable : {filepath}")
        return None, 0

    file_size = os.path.getsize(filepath)
    print(f"Fichier : {filepath} ({file_size/1e9:.1f} Go)")
    print()

    groups = defaultdict(list)
    processed = 0
    last_print = 0
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

            uid = raw.get("uid", "unknown")
            ts = raw.get("time")

            # Mini-événement avec les champs nécessaires à extract_features()
            groups[uid].append({
                "timestamp": ts,
                "source_ip": raw.get("ip", "0.0.0.0"),
                "log_type": raw.get("type", "application"),
                "severity": "info",
                "decoded": {"user": uid},
                "raw_data": {"uid": uid},
            })

            processed += 1

            if processed - last_print >= 200000:
                elapsed = time.time() - start
                rate = processed / elapsed if elapsed > 0 else 0
                mem_mb = sum(sys.getsizeof(v) for v in groups.values()) / (1024 * 1024)
                print(f"  {processed} events | {len(groups)} users | {mem_mb:.0f} MB | {rate:.0f} evt/s")
                last_print = processed

            if sample and processed >= sample:
                print(f"  Limite atteinte ({sample})")
                break

    elapsed = time.time() - start
    rate = processed / elapsed if elapsed > 0 else 0
    print(f"\nCharge    : {processed} evenements en {elapsed:.1f}s ({rate:.0f} evt/s)")
    print(f"Entites   : {len(groups)} utilisateurs")

    return dict(groups), processed


# ===========================================================================
# MODE ES
# ===========================================================================


async def load_from_es(index: str, batch_size: int = 5000, sample: int = None):
    """Charge les événements depuis Elasticsearch via search_after."""
    from elasticsearch import AsyncElasticsearch

    es = AsyncElasticsearch(["http://localhost:9200"])

    if not await es.indices.exists(index=index):
        print(f"Index '{index}' introuvable.")
        await es.close()
        return None, 0

    count_resp = await es.count(index=index)
    total_es = count_resp["count"]
    print(f"Index    : {index}")
    print(f"Total ES : {total_es} evenements")
    print()

    last_sort = None
    groups = defaultdict(list)
    processed = 0
    last_print = 0

    while True:
        body = {
            "query": {"match_all": {}},
            "size": batch_size,
            "sort": ["_doc"],
            "_source": ["timestamp", "source_ip", "log_type", "severity", "decoded.user", "raw_data.uid"],
        }
        if last_sort:
            body["search_after"] = last_sort

        resp = await es.search(
            index=index, body=body,
            filter_path=["hits.hits._source", "hits.hits.sort", "hits.total"],
        )
        hits = resp.get("hits", {}).get("hits", []) if resp else []

        if not hits:
            break

        for hit in hits:
            e = hit["_source"]
            entity_id = (
                e.get("decoded", {}).get("user")
                or e.get("raw_data", {}).get("uid")
                or e.get("source_ip", "unknown")
            )
            groups[entity_id].append({
                "timestamp": e.get("timestamp"),
                "source_ip": e.get("source_ip"),
                "log_type": e.get("log_type"),
                "severity": e.get("severity"),
                "decoded": {"user": e.get("decoded", {}).get("user")},
                "raw_data": {"uid": e.get("raw_data", {}).get("uid")},
            })

        processed += len(hits)
        last_sort = hits[-1]["sort"]

        if processed - last_print >= 100000:
            mem_mb = sum(sys.getsizeof(v) for v in groups.values()) / (1024 * 1024)
            print(f"  {processed}/{total_es} events | {len(groups)} users | {mem_mb:.0f} MB")
            last_print = processed

        if sample and processed >= sample:
            print(f"  Limite atteinte ({sample})")
            break

    await es.close()

    print(f"\nCharge    : {processed} evenements")
    print(f"Entites   : {len(groups)} utilisateurs")
    return dict(groups), processed


# ===========================================================================
# ENTRAÎNEMENT
# ===========================================================================


async def train_model(groups: dict, processed: int):
    """Entraîne et sauvegarde le modèle, met à jour les profils."""
    if not groups or len(groups) < 5:
        print("Pas assez d'entites (< 5).")
        return

    print(f"\nEntrainement Isolation Forest sur {len(groups)} entites...")
    start = time.time()

    async with async_session_factory() as db:
        result = await ueba_service.train_model(groups, db)
        await db.commit()

    elapsed = time.time() - start
    print(f"Entrainement : {elapsed:.1f}s")
    print(f"Statut       : {result.get('status')}")
    print(f"Entites      : {result.get('entities_trained')}")
    print(f"Modele       : {result.get('model_path')}")


# ===========================================================================
# POINT D'ENTRÉE
# ===========================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entrainement du modele UEBA")
    parser.add_argument("--file", help="Fichier clue.json (lecture directe, recommande)")
    parser.add_argument("--index", help="Index Elasticsearch (logs-clue)")
    parser.add_argument("--sample", type=int, default=None, help="Limite d'evenements")
    parser.add_argument("--batch", type=int, default=5000, help="Taille du lot ES")
    args = parser.parse_args()

    print("=" * 50)
    print("  ENTRAINEMENT UEBA")
    print("=" * 50)
    print()

    groups = None
    processed = 0

    if args.file:
        # Mode fichier (recommandé)
        groups, processed = load_from_file(args.file, args.sample)
    elif args.index:
        # Mode ES (fallback)
        groups, processed = asyncio.run(load_from_es(args.index, args.batch, args.sample))
    else:
        print("Utilise --file ou --index")
        parser.print_help()
        sys.exit(1)

    if groups and processed > 0:
        asyncio.run(train_model(groups, processed))
    else:
        print("Rien a entrainer.")
