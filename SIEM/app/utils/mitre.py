# app/utils/mitre.py
# -------------------------------
# Referentiel MITRE ATT&CK (constantes et mappings)

from typing import List, Optional

# Mapping des techniques MITRE ATT&CK avec leur nom et tactique
MITRE_ATTACK_DATA = {
    # Reconnaissance (TA0043)
    "T1046": {"name": "Network Service Scanning", "tactic": "reconnaissance"},
    "T1595": {"name": "Active Scanning", "tactic": "reconnaissance"},
    # Initial Access (TA0001)
    "T1078": {"name": "Valid Accounts", "tactic": "initial_access"},
    "T1110": {"name": "Brute Force", "tactic": "credential_access"},
    "T1110.001": {"name": "Password Guessing", "tactic": "credential_access"},
    "T1110.003": {"name": "Credential Stuffing", "tactic": "credential_access"},
    "T1133": {"name": "External Remote Services", "tactic": "initial_access"},
    "T1190": {"name": "Exploit Public-Facing Application", "tactic": "initial_access"},
    "T1566": {"name": "Phishing", "tactic": "initial_access"},
    # Execution (TA0002)
    "T1059": {"name": "Command and Scripting Interpreter", "tactic": "execution"},
    "T1059.001": {"name": "PowerShell", "tactic": "execution"},
    "T1204": {"name": "User Execution", "tactic": "execution"},
    # Persistence (TA0003)
    "T1098": {"name": "Account Manipulation", "tactic": "persistence"},
    "T1136": {"name": "Create Account", "tactic": "persistence"},
    "T1574": {"name": "Hijack Execution Flow", "tactic": "persistence"},
    # Defense Evasion (TA0005)
    "T1070": {"name": "Indicator Removal", "tactic": "defense_evasion"},
    "T1070.001": {"name": "Clear Windows Event Logs", "tactic": "defense_evasion"},
    "T1070.004": {"name": "File Deletion", "tactic": "defense_evasion"},
    "T1134": {"name": "Access Token Manipulation", "tactic": "defense_evasion"},
    "T1562": {"name": "Impair Defenses", "tactic": "defense_evasion"},
    "T1562.001": {"name": "Disable or Modify Tools", "tactic": "defense_evasion"},
    "T1562.002": {"name": "Disable Windows Event Logging", "tactic": "defense_evasion"},
    # Credential Access (TA0006)
    "T1110": {"name": "Brute Force", "tactic": "credential_access"},
    "T1555": {
        "name": "Credentials from Password Stores",
        "tactic": "credential_access",
    },
    # Discovery (TA0007)
    "T1082": {"name": "System Information Discovery", "tactic": "discovery"},
    # Lateral Movement (TA0008)
    "T1210": {"name": "Exploitation of Remote Services", "tactic": "lateral_movement"},
    "T1550": {
        "name": "Use Alternate Authentication Material",
        "tactic": "lateral_movement",
    },
    "T1550.002": {"name": "Pass-the-Hash", "tactic": "lateral_movement"},
    "T1021": {"name": "Remote Services", "tactic": "lateral_movement"},
    "T1021.002": {"name": "SMB/Windows Admin Shares", "tactic": "lateral_movement"},
    # Collection (TA0009)
    "T1530": {"name": "Data from Cloud Storage", "tactic": "collection"},
    "T1005": {"name": "Data from Local System", "tactic": "collection"},
    # Exfiltration (TA0010)
    "T1041": {"name": "Exfiltration Over C2 Channel", "tactic": "exfiltration"},
    "T1048": {
        "name": "Exfiltration Over Alternative Protocol",
        "tactic": "exfiltration",
    },
    "T1567": {"name": "Exfiltration Over Web Service", "tactic": "exfiltration"},
    # Impact (TA0040)
    "T1485": {"name": "Data Destruction", "tactic": "impact"},
    "T1486": {"name": "Data Encrypted for Impact", "tactic": "impact"},
}

# Liste complete des tactiques MITRE ATT&CK Enterprise v14+
MITRE_TACTICS = [
    "reconnaissance",
    "resource_development",
    "initial_access",
    "execution",
    "persistence",
    "privilege_escalation",
    "defense_evasion",
    "credential_access",
    "discovery",
    "lateral_movement",
    "collection",
    "command_and_control",
    "exfiltration",
    "impact",
]


def get_mitre_technique(technique_id: str) -> Optional[dict]:
    """Retourne les infos d'une technique MITRE."""
    return MITRE_ATTACK_DATA.get(technique_id.upper())


def get_techniques_by_tactic(tactic: str) -> List[dict]:
    """Liste les techniques d'une tactique donnee."""
    return [
        {"id": k, **v}
        for k, v in MITRE_ATTACK_DATA.items()
        if v.get("tactic") == tactic
    ]


def get_all_techniques() -> List[dict]:
    """Retourne toutes les techniques MITRE."""
    return [{"id": k, **v} for k, v in MITRE_ATTACK_DATA.items()]


def get_tactics() -> List[str]:
    """Retourne la liste de toutes les tactiques."""
    return MITRE_TACTICS.copy()
