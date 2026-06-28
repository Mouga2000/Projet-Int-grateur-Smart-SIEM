# app/utils/mitre.py
# -------------------------------
# Référentiel MITRE ATT&CK (constantes et mappings)
#
# Ce que tu dois mettre ici :
#
#   # Mapping des techniques MITRE ATT&CK avec leur nom et catégorie
#
#   MITRE_ATTACK_DATA = {
#       "T1059": {
#           "name": "Command and Scripting Interpreter",
#           "tactic": "execution",
#           "platforms": ["windows", "linux", "macos"],
#       },
#       "T1059.001": {
#           "name": "PowerShell",
#           "parent": "T1059",
#           "tactic": "execution",
#       },
#       "T1078": {
#           "name": "Valid Accounts",
#           "tactic": "defense_evasion",
#       },
#       "T1078.001": {
#           "name": "Default Accounts",
#           "parent": "T1078",
#       },
#       "T1078.002": {"name": "Domain Accounts", "parent": "T1078"},
#       "T1078.003": {"name": "Local Accounts", "parent": "T1078"},
#       "T1078.004": {"name": "Cloud Accounts", "parent": "T1078"},
#       "T1098": {"name": "Account Manipulation", "tactic": "persistence"},
#       "T1110": {"name": "Brute Force", "tactic": "credential_access"},
#       "T1110.001": {"name": "Password Guessing", "parent": "T1110"},
#       "T1110.002": {"name": "Password Spraying", "parent": "T1110"},
#       "T1110.003": {"name": "Credential Stuffing", "parent": "T1110"},
#       "T1133": {"name": "External Remote Services", "tactic": "initial_access"},
#       "T1134": {"name": "Access Token Manipulation", "tactic": "defense_evasion"},
#       "T1190": {"name": "Exploit Public-Facing Application", "tactic": "initial_access"},
#       "T1204": {"name": "User Execution", "tactic": "execution"},
#       "T1204.002": {"name": "Malicious File", "parent": "T1204"},
#       "T1210": {"name": "Exploitation of Remote Services", "tactic": "lateral_movement"},
#       "T1485": {"name": "Data Destruction", "tactic": "impact"},
#       "T1486": {"name": "Data Encrypted for Impact", "tactic": "impact"},
#       "T1530": {"name": "Data from Cloud Storage", "tactic": "collection"},
#       "T1566": {"name": "Phishing", "tactic": "initial_access"},
#       "T1566.001": {"name": "Spearphishing Attachment", "parent": "T1566"},
#       "T1566.002": {"name": "Spearphishing Link", "parent": "T1566"},
#       "T1568": {"name": "Dynamic Resolution", "tactic": "command_and_control"},
#       "T1574": {"name": "Hijack Execution Flow", "tactic": "persistence"},
#       "T1580": {"name": "Cloud Infrastructure Discovery", "tactic": "discovery"},
#       "T1583": {"name": "Acquire Infrastructure", "tactic": "resource_development"},
#       "T1587": {"name": "Develop Capabilities", "tactic": "resource_development"},
#       # ... à compléter avec la matrice complète MITRE ATT&CK v14+
#   }
#
#   def get_mitre_technique(technique_id: str) -> dict | None:
#       """Retourne les infos d'une technique MITRE."""
#       return MITRE_ATTACK_DATA.get(technique_id.upper())
#
#   def get_techniques_by_tactic(tactic: str) -> list[dict]:
#       """Liste les techniques d'une tactique donnée."""
#       return [v for v in MITRE_ATTACK_DATA.values() if v.get("tactic") == tactic]
#
#   MITRE_TACTICS = [
#       "reconnaissance",
#       "resource_development",
#       "initial_access",
#       "execution",
#       "persistence",
#       "privilege_escalation",
#       "defense_evasion",
#       "credential_access",
#       "discovery",
#       "lateral_movement",
#       "collection",
#       "command_and_control",
#       "exfiltration",
#       "impact",
#   ]
