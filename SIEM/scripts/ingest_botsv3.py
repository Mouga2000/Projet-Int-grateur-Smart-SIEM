#!/usr/bin/env python3
"""
Ingestion du dataset BOTSv3 via l'API SmartSIEM (bulk-ingest).

Extrait les données des fichiers journal.gz (Splunk coldDB), mappe chaque
document au format brut attendu par le backend, puis envoie par lots
à /api/v1/logs/bulk-ingest. Chaque lot passe par NormalizationService.

Usage :
    python scripts/ingest_botsv3.py                    # tout le dataset
    python scripts/ingest_botsv3.py --limit 10000      # seulement 10k logs
    python scripts/ingest_botsv3.py --batch-size 1000  # lots de 1000
"""

import argparse
import email.utils
import gzip
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# ─── Configuration ────────────────────────────────────────────────────────────

API_BASE = "http://127.0.0.1:8000/api/v1"
BATCH_SIZE = 500       # Logs par requête bulk
BOTS_DIR = Path(__file__).resolve().parent.parent / "docs" / "botsv3_data_set"


# ─── Authentification ─────────────────────────────────────────────────────────

class ApiSession:
    """Gère l'authentification et les appels à l'API."""

    def __init__(self, api_base: str, username: str, password: str):
        self.api_base = api_base
        self.username = username
        self.password = password
        self.token = None
        self.http = requests.Session()

    def login(self):
        resp = self.http.post(
            f"{self.api_base}/auth/login",
            json={"username": self.username, "password": self.password},
            timeout=10,
        )
        resp.raise_for_status()
        self.token = resp.json()["access_token"]
        self.http.headers.update({"Authorization": f"Bearer {self.token}"})

    def bulk_ingest(self, logs: list[dict]) -> dict:
        """Envoie un lot de logs bruts au endpoint d'ingestion (mode bulk)."""
        resp = self.http.post(
            f"{self.api_base}/logs/ingest",
            json=logs,
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()


# ─── Extraction des fichiers Splunk journal.gz ────────────────────────────────

def extract_json_from_journal(raw: bytes) -> list[dict]:
    """Extrait les objets JSON des fichiers journal.gz (binaire + JSON)."""
    docs = []
    for m in re.finditer(rb'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}', raw):
        try:
            doc = json.loads(m.group(0).decode("utf-8", errors="replace"))
            if isinstance(doc, dict) and len(doc) >= 2:
                docs.append(doc)
        except (json.JSONDecodeError, ValueError):
            pass
    return docs


# ─── Mapping BOTSv3 → format brut attendu par l'API ──────────────────────────

def normalize_timestamp(ts) -> str:
    """Convertit différents formats de timestamp en ISO 8601."""
    if not ts:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(ts, (int, float)):
        try:
            return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, OSError):
            return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(ts, str):
        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", ts):
            return ts
        try:
            parsed = email.utils.parsedate_to_datetime(ts)
            return parsed.strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError):
            pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def map_to_api_format(entry: dict) -> dict | None:
    """
    Mappe un document BOTSv3 brut au format attendu par /api/v1/logs/bulk-ingest.

    Le NormalizationService du backend utilise :
      - raw_message : analysé par les regex de sévérité
      - host        : la machine source
      - source_ip   : l'IP source
      - timestamp   : horodatage ISO 8601
      - event_type  : surclasse log_type auto si présent
    """
    if not entry:
        return None

    raw_json = json.dumps(entry, ensure_ascii=False)

    # Host
    host = entry.get("hostIdentifier") or entry.get("deviceAddress") or \
           entry.get("host") or entry.get("region", "unknown")

    # Source IP
    source_ip = "0.0.0.0"
    if "columns" in entry and isinstance(entry["columns"], dict):
        source_ip = entry["columns"].get("address",
                    entry["columns"].get("ip",
                    entry["columns"].get("dst_ip", source_ip)))
    source_ip = entry.get("src_ip", source_ip)
    source_ip = entry.get("deviceAddress", source_ip)
    source_ip = entry.get("source_ip", source_ip)

    # Timestamp (essayer tous les formats présents dans BOTSv3)
    raw_ts = entry.get("calendarTime") or entry.get("formattedTimestamp") or \
             entry.get("timestamp", "")
    timestamp = normalize_timestamp(raw_ts)

    # Event type (aide le normalizer à mieux classer)
    event_type = None
    if "eventType" in entry:
        event_type = entry["eventType"]
    elif "name" in entry:
        name = entry.get("name", "")
        if isinstance(name, str):
            nl = name.lower()
            if "suricata" in nl or "snort" in nl:
                event_type = "ids"
            elif "dns" in nl:
                event_type = "dns"
            elif "http" in nl or "web" in nl:
                event_type = "web"
            elif "ssh" in nl:
                event_type = "ssh"
            elif "windows-attacks" in nl:
                event_type = "windows_attack"
        if not event_type:
            event_type = "osquery"
    elif "flow_id" in entry:
        event_type = "network_flow"
        # Suricata : utiliser le timestamp existant comme raw_message indicatif
        source_ip = entry.get("src_ip", entry.get("dest_ip", source_ip))
    elif any(k in entry for k in ("region", "account_id", "InstanceId")):
        event_type = "aws_inventory"

    return {
        "raw_message": raw_json,
        "host": host,
        "source_ip": source_ip,
        "timestamp": timestamp,
        **({"event_type": event_type} if event_type else {}),
    }


# ─── Parcours et ingestion ─────────────────────────────────────────────────────

def find_journal_files():
    """Trouve tous les fichiers journal.gz dans le dataset BOTSv3."""
    files = sorted(BOTS_DIR.glob("**/rawdata/journal.gz"))
    return files or sorted(BOTS_DIR.glob("**/journal.gz"))


def process_file(filepath: Path, api: ApiSession, batch_size: int,
                 limit: int = 0) -> tuple[int, int, list[str]]:
    """
    Traite un fichier journal.gz : extraction → mapping → bulk via API.
    Retourne (trouvés, indexés, [erreurs]).
    """
    try:
        with gzip.open(filepath, "rb") as f:
            raw = f.read()
    except Exception as e:
        return 0, 0, [f"Erreur lecture: {e}"]

    entries = extract_json_from_journal(raw)
    if not entries:
        return 0, 0, []

    mapped = []
    for entry in entries:
        doc = map_to_api_format(entry)
        if doc:
            mapped.append(doc)
            if limit and len(mapped) >= limit:
                break

    if not mapped:
        return len(entries), 0, []

    indexed = 0
    errors = []

    # Envoyer par lots au bulk-ingest
    for i in range(0, len(mapped), batch_size):
        batch = mapped[i : i + batch_size]
        try:
            result = api.bulk_ingest(batch)
            indexed += result.get("indexed", 0)
            for err in result.get("errors", []):
                errors.append(f"[{err['index']}] {err['error']}")
                if len(errors) >= 10:
                    break
        except requests.exceptions.RequestException as e:
            errors.append(str(e)[:150])
            if len(errors) >= 5:
                break

    return len(mapped), indexed, errors


def main():
    parser = argparse.ArgumentParser(description="Ingestion BOTSv3 via l'API SmartSIEM")
    parser.add_argument("--limit", type=int, default=0, help="Nombre max de logs")
    parser.add_argument("--api", default=API_BASE, help=f"Base URL API (défaut: {API_BASE})")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE,
                        help=f"Logs par requête bulk (défaut: {BATCH_SIZE})")
    parser.add_argument("--username", default="AdminBobi", help="Identifiant")
    parser.add_argument("--password", default="admin123", help="Mot de passe")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  BOTSv3 -> {args.api}/logs/ingest (mode bulk)")
    print(f"  Batch size : {args.batch_size}")
    print(f"  Limite     : {'aucune' if args.limit == 0 else args.limit}")
    print(f"{'='*60}")

    # Connexion
    api = ApiSession(args.api, args.username, args.password)
    try:
        api.login()
        print(f"  ✓ Connecté ({args.username})\n")
    except Exception as e:
        print(f"  ✗ Authentification: {e}")
        sys.exit(1)

    # Fichiers
    journal_files = find_journal_files()
    if not journal_files:
        print(f"  ✗ Aucun fichier journal.gz dans {BOTS_DIR}")
        sys.exit(1)
    print(f"  {len(journal_files)} fichier(s)\n")

    total_found = 0
    total_indexed = 0
    start_time = time.time()

    for fp in journal_files:
        rel = fp.relative_to(BOTS_DIR)
        sys.stdout.write(f"  [{rel}]")
        sys.stdout.flush()

        found, indexed, errors = process_file(
            fp, api, args.batch_size,
            args.limit - total_indexed if args.limit else 0
        )

        total_found += found
        total_indexed += indexed

        pieces = [f" {indexed}/{found}"]
        if errors:
            pieces.append(f" ({len(errors)} err)")
        print(f" →{''.join(pieces)}")

        if errors:
            for e in errors[:3]:
                print(f"      ⚠ {e}")

        if args.limit and total_indexed >= args.limit:
            print(f"\n  ✓ Limite atteinte ({args.limit} logs)")
            break

    elapsed = time.time() - start_time
    rate = total_indexed / elapsed if elapsed > 0 else 0

    print(f"\n{'='*60}")
    print(f"  Résumé")
    print(f"  Trouvés  : {total_found}")
    print(f"  Indexés  : {total_indexed}")
    print(f"  Temps    : {elapsed:.1f}s")
    print(f"  Débit    : {rate:.1f} logs/s")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
