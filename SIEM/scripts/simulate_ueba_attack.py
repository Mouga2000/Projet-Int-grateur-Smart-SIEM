#!/usr/bin/env python3
"""
Simule un détournement de compte pour valider le module UEBA.

Principe :
  1. Prend des événements d'autres utilisateurs du dataset CLUE-LDS
  2. Les injecte dans le SIEM sous l'identité d'un utilisateur cible
  3. Le modèle UEBA devrait détecter l'anomalie et faire monter le score

Utilisation :
    python scripts/simulate_ueba_attack.py user_cible clue.json

Options :
    --count 200    Nombre d'événements à injecter (défaut: 100)

Exemple :
    python scripts/simulate_ueba_attack.py \
        "intact-gray-marlin-trademarkagent" clue.json --count 150

Vérification :
    # Avant : score bas
    curl http://localhost:8000/api/v1/ueba/profile/user_cible

    # Pendant : le score devrait monter > 70
    curl http://localhost:8000/api/v1/ueba/profile/user_cible

    # Liste des scores
    curl http://localhost:8000/api/v1/ueba/scores?min_score=50
"""

import json
import os
import random
import sys
import time
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx

API_URL = "http://localhost:8000/api/v1/logs/ingest"


def load_events(filepath: str) -> List[dict]:
    """Charge les événements depuis le fichier CLUE-LDS."""
    events = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return events


def simulate(target: str, filepath: str, count: int = 100):
    """
    Injecte des événements d'autres utilisateurs sous l'identité de la cible.

    Args:
        target: Identifiant de l'utilisateur cible (champ "uid" dans CLUE-LDS)
        filepath: Chemin vers le fichier clue.json
        count: Nombre d'événements à injecter
    """
    print(f"Cible    : {target}")
    print(f"Fichier  : {filepath}")
    print(f"Evenements : {count}")
    print(f"---")

    # Charger tous les événements
    all_events = load_events(filepath)
    print(f"Dataset charge : {len(all_events)} evenements")

    # Filtrer : garder uniquement les événements d'AUTRES utilisateurs
    others = [e for e in all_events if e.get("uid") != target]
    if not others:
        print(f"Aucun evenement d'autres utilisateurs trouve.")
        sys.exit(1)

    print(f"Evenements d'autres utilisateurs : {len(others)}")

    # Selection aléatoire
    selected = random.sample(others, min(count, len(others)))
    print(f"Selectionnes : {len(selected)} (injection en cours...)")

    # Injection
    success = 0
    start = time.time()

    for e in selected:
        doc = {
            "source_ip": f"10.0.{random.randint(1,254)}.{random.randint(1,254)}",
            "host": target,
            "log_type": e.get("type", "application"),
            "severity": "critical",
            "raw_message": json.dumps(e, default=str),
            "timestamp": e.get("time"),
            "raw_data": {
                "uid": target,
                "original_uid": e.get("uid"),
                "role": e.get("role"),
                "simulation": True,
            },
        }
        try:
            resp = httpx.post(API_URL, json=doc, timeout=10)
            if resp.status_code == 200:
                success += 1
                print(".", end="", flush=True)
        except Exception:
            print("x", end="", flush=True)

    elapsed = time.time() - start
    print(f"\n---")
    print(f"Injecte : {success}/{len(selected)} evenements en {elapsed:.1f}s")
    print(f"")
    print(f"Verifie le profil UEBA de la cible :")
    print(f"  curl http://localhost:8000/api/v1/ueba/profile/{target}")
    print(f"")
    print(f"Le score devrait avoir augmente significativement (> 70).")


if __name__ == "__main__":
    target = None
    filepath = None
    count = 100

    args = sys.argv[1:]
    positional = [a for a in args if not a.startswith("--")]

    if len(positional) >= 1:
        target = positional[0]
    if len(positional) >= 2:
        filepath = positional[1]

    if not target or not filepath:
        print(__doc__)
        sys.exit(1)

    for i, arg in enumerate(args):
        if arg == "--count" and i + 1 < len(args):
            count = int(args[i + 1])

    simulate(target, filepath, count)
