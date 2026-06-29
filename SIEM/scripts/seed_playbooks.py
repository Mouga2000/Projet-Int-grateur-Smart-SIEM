#!/usr/bin/env python3
# scripts/seed_playbooks.py
# -------------------------------
# Script d'initialisation des playbooks SOAR par defaut

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import async_session_factory
from app.repositories.playbook_repo import PlaybookRepository

DEFAULT_PLAYBOOKS = [
    {
        "name": "Bloquer IP malveillante",
        "description": "Bloque une IP source via le pare-feu de la machine cible. Utile pour stopper une attaque en cours (brute force, scan, etc.).",
        "trigger": "manual",
        "steps": [
            {
                "action": "block_ip",
                "params": {
                    "ip": "{{source_ip}}",
                    "comment": "Blocage SOAR automatique",
                },
            },
            {
                "action": "notify_slack",
                "params": {
                    "channel": "#security",
                    "message": "[SOAR] IP {{source_ip}} bloquee sur {{host}}",
                },
            },
        ],
        "timeout_seconds": 30,
        "max_retries": 2,
    },
    {
        "name": "Desactiver compte compromise",
        "description": "Desactive un compte utilisateur suspect sur la machine cible et cree un ticket.",
        "trigger": "manual",
        "steps": [
            {
                "action": "disable_user",
                "params": {"username": "{{user}}"},
            },
            {
                "action": "create_ticket",
                "params": {
                    "title": "Compte compromis: {{user}}",
                    "description": "Compte desactive automatiquement par SOAR",
                },
            },
        ],
        "timeout_seconds": 30,
        "max_retries": 2,
    },
    {
        "name": "Isoler machine compromise",
        "description": "Isole completement un hote du reseau (trafic entrant et sortant bloque). Utilise en cas d'infection ou de compromission avancee.",
        "trigger": "alert_created",
        "steps": [
            {
                "action": "isolate_host",
                "params": {},
            },
            {
                "action": "notify_slack",
                "params": {
                    "channel": "#security",
                    "message": "[SOAR] Hote {{host}} isole du reseau",
                },
            },
        ],
        "timeout_seconds": 30,
        "max_retries": 1,
    },
]


async def seed_playbooks():
    """Insere les playbooks par defaut si ils n'existent pas."""
    print("Initialisation des playbooks SOAR...")
    async with async_session_factory() as db:
        repo = PlaybookRepository(db)
        created = 0
        skipped = 0
        for pb_data in DEFAULT_PLAYBOOKS:
            existing = await repo.get_enabled_playbooks()
            already_exists = any(p["name"] == pb_data["name"] for p in existing)
            if not already_exists:
                await repo.create(pb_data)
                print(f"  [CREEE] {pb_data['name']}")
                created += 1
            else:
                print(f"  [EXISTE] {pb_data['name']}")
                skipped += 1
        await db.commit()
        print(f"\nTermine : {created} playbooks crees, {skipped} deja existants.")


if __name__ == "__main__":
    asyncio.run(seed_playbooks())
