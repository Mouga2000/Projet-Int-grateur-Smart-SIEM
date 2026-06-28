#!/usr/bin/env python3
# scripts/seed_rules.py
# -------------------------------
# Script d'initialisation des regles de correlation par defaut
# Couvre les scenarios MITRE ATT&CK requis

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import async_session_factory
from app.repositories.rule_repo import RuleRepository

DEFAULT_RULES = [
    # =========================================================================
    # S3 — Chloe : Initial Access / Brute Force (T1110)
    # 5 echecs auth en 60s sur la meme cible
    # =========================================================================
    {
        "name": "Brute Force - 5 echecs auth en 60s",
        "description": "Detecte les tentatives de bruteforce (>5 echecs d'authentification en 60 secondes sur la meme cible). Ref MITRE T1110 - Brute Force. Scenario CTU S3 - Chloe.",
        "rule_type": "threshold",
        "severity": "high",
        "priority": 90,
        "condition": {"field": "log_type", "value": "auth", "group_by": "source_ip"},
        "threshold": {"count": 5, "window_seconds": 60},
        "mitre_tactic": "credential_access",
        "mitre_technique": "T1110",
        "actions": {"create_alert": True},
        "enabled": True,
    },
    # =========================================================================
    # S6 — Tony : Lateral Movement / Pass-the-Hash (T1550)
    # Authentification NTLM inhabituelle entre 2 postes internes
    # =========================================================================
    {
        "name": "Pass-the-Hash - Lateral Movement",
        "description": "Detecte une authentification NTLM inhabituelle entre deux postes internes, pouvant indiquer un mouvement lateral Pass-the-Hash. Ref MITRE T1550 - Use Alternate Authentication Material. Scenario CTU S6 - Tony.",
        "rule_type": "threshold",
        "severity": "critical",
        "priority": 95,
        "condition": {"field": "log_type", "value": "reseau", "group_by": "source_ip"},
        "threshold": {"count": 3, "window_seconds": 300},
        "mitre_tactic": "lateral_movement",
        "mitre_technique": "T1550",
        "actions": {"create_alert": True},
        "enabled": True,
    },
    # =========================================================================
    # S7 — Nina Myers : Exfiltration / Exfiltration Over C2 (T1041)
    # Volume de donnees sortant > 10x la baseline sur 15 min
    # =========================================================================
    {
        "name": "Exfiltration - Volume C2 anormal",
        "description": "Detecte un volume de donnees sortant anormal (>10x la moyenne) sur une fenetre de 15 minutes, pouvant indiquer une exfiltration via canal C2. Ref MITRE T1041 - Exfiltration Over C2 Channel. Scenario CTU S7 - Nina Myers.",
        "rule_type": "threshold",
        "severity": "critical",
        "priority": 100,
        "condition": {"field": "log_type", "value": "systeme", "group_by": "host"},
        "threshold": {"count": 10, "window_seconds": 900},
        "mitre_tactic": "exfiltration",
        "mitre_technique": "T1041",
        "actions": {"create_alert": True},
        "enabled": True,
    },
    # =========================================================================
    # Defense Evasion / Log Deletion (T1070)
    # Arret du service de journalisation sur un endpoint
    # =========================================================================
    {
        "name": "Log Deletion - Arret journalisation",
        "description": "Detecte l'arret du service de journalisation sur un endpoint, pouvant indiquer une tentative de effacement de traces (Log Deletion). Ref MITRE T1070 - Indicator Removal.",
        "rule_type": "single_event",
        "severity": "high",
        "priority": 85,
        "condition": {
            "field": "raw_message",
            "value": "Service Windows Event Log stopped",
        },
        "mitre_tactic": "defense_evasion",
        "mitre_technique": "T1070",
        "actions": {"create_alert": True},
        "enabled": True,
    },
    # =========================================================================
    # Port Scanning / Reconnaissance (T1046)
    # =========================================================================
    {
        "name": "Port Scan - Reconnaissance",
        "description": "Detecte un scan de ports (>10 connexions vers des ports differents en 30s depuis la meme IP). Ref MITRE T1046 - Network Service Scanning.",
        "rule_type": "threshold",
        "severity": "medium",
        "priority": 70,
        "condition": {"field": "log_type", "value": "reseau", "group_by": "source_ip"},
        "threshold": {"count": 10, "window_seconds": 30},
        "mitre_tactic": "reconnaissance",
        "mitre_technique": "T1046",
        "actions": {"create_alert": True},
        "enabled": True,
    },
    # =========================================================================
    # Correlation inter-sources : Firewall + Active Directory (T1078)
    # Un evenement pare-feu suivi d'une authentification AD depuis la meme IP
    # =========================================================================
    {
        "name": "Firewall + AD - Correlation multi-sources",
        "description": "Correlation : un evenement pare-feu (IP bloquee) suivi d'une authentification AD depuis la meme IP en moins de 5 min. Ref MITRE T1078 - Valid Accounts.",
        "rule_type": "correlation",
        "severity": "critical",
        "priority": 95,
        "condition": {
            "link_by": "source_ip",
            "window_minutes": 5,
            "min_events": 2,
        },
        "mitre_tactic": "initial_access",
        "mitre_technique": "T1078",
        "actions": {"create_alert": True},
        "enabled": True,
    },
    # =========================================================================
    # Sequence : Reconnaissance -> Lateral Movement -> Exfiltration
    # Pattern de detection d'une chaine d'attaque complete
    # =========================================================================
    {
        "name": "Attaque complete - Recon -> Lateral -> Exfil",
        "description": "Sequence typique d'attaque : scan de ports (reconnaissance) -> connexion inter-hote (lateral movement) -> volume sortant anormal (exfiltration). Ref MITRE T1046 -> T1550 -> T1041.",
        "rule_type": "sequence",
        "severity": "critical",
        "priority": 100,
        "condition": {},
        "steps": [
            {"log_type": "reseau", "severity": "medium"},
            {"log_type": "reseau", "severity": "warning"},
            {"log_type": "systeme", "severity": "high"},
        ],
        "window_seconds": 600,
        "group_by": "source_ip",
        "mitre_tactic": "exfiltration",
        "mitre_technique": "T1041",
        "actions": {"create_alert": True},
        "enabled": True,
    },
]


async def seed_rules():
    """Insere les regles par defaut si elles n'existent pas."""
    print("Initialisation des regles de correlation...")
    async with async_session_factory() as db:
        repo = RuleRepository(db)
        created = 0
        skipped = 0
        for rule_data in DEFAULT_RULES:
            # Verifier si une regle avec le meme nom existe deja
            existing_rules = await repo.get_enabled_rules()
            already_exists = any(r["name"] == rule_data["name"] for r in existing_rules)
            if not already_exists:
                await repo.create(rule_data)
                print(f"  [CREEE] {rule_data['name']}")
                created += 1
            else:
                print(f"  [EXISTE] {rule_data['name']}")
                skipped += 1
        await db.commit()
        print(f"\nTermine : {created} regles creees, {skipped} deja existantes.")


if __name__ == "__main__":
    asyncio.run(seed_rules())
