#!/usr/bin/env python3
# scripts/seed_rules.py
# -------------------------------
# Script d'initialisation des règles de corrélation par défaut
#
# Ce script crée les règles de base pour la détection :
#   - Tentatives de bruteforce SSH (seuil)
#   - Port scanning
#   - Connexions depuis des IP suspectes
#   - Exécution de commandes suspectes (PowerShell, WMI)
#   - Création de comptes utilisateur
#   - Accès hors horaires de travail
#   - Téléchargements massifs (exfiltration potentielle)
#   - Règles MITRE ATT&CK correspondantes
#
# Ce que tu dois mettre ici :
#
#   import asyncio
#   import json
#   from app.core.database import async_session_factory
#   from app.repositories.rule_repo import RuleRepository
#   from app.models.rule import RuleType
#
#   DEFAULT_RULES = [
#       {
#           "name": "SSH Bruteforce Detection",
#           "description": "Détecte les tentatives de bruteforce SSH (>5 échecs en 5 min)",
#           "rule_type": "threshold",
#           "severity": "high",
#           "mitre_attack_id": "T1110",
#           "condition": {
#               "field": "event_type",
#               "value": "ssh_failed_login",
#               "threshold": 5,
#               "window_minutes": 5,
#           },
#           "actions": {"create_alert": True, "notify_slack": True, "run_playbook": 1},
#       },
#       {
#           "name": "Port Scan Detection",
#           "description": "Détecte les scans de ports (>20 ports en 1 min)",
#           "rule_type": "threshold",
#           "severity": "medium",
#           "mitre_attack_id": "T1046",
#           "condition": {
#               "field": "event_type",
#               "value": "connection_attempt",
#               "threshold": 20,
#               "window_minutes": 1,
#               "group_by": "source_ip",
#           },
#           "actions": {"create_alert": True},
#       },
#       # ... à compléter
#   ]
#
#   async def seed_rules():
#       """Insère les règles par défaut si elles n'existent pas."""
#       async with async_session_factory() as db:
#           repo = RuleRepository(db)
#           for rule_data in DEFAULT_RULES:
#               existing = await repo.get_multi(filters={"name": rule_data["name"]})
#               if not existing:
#                   await repo.create(rule_data)
#                   print(f"  ✓ Règle créée : {rule_data['name']}")
#               else:
#                   print(f"  - Déjà existante : {rule_data['name']}")
#
#   if __name__ == "__main__":
#       asyncio.run(seed_rules())
