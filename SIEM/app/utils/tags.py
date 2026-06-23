# app/utils/tags.py
# -------------------------------
# Tags de criticité, type de log, et constantes
#
# Ce que tu dois mettre ici :
#
#   CRITICITY_TAGS = {
#       "critical": {"color": "red", "priority": 5, "description": "Menace immédiate"},
#       "high": {"color": "orange", "priority": 4, "description": "Menace sérieuse"},
#       "medium": {"color": "yellow", "priority": 3, "description": "Menace potentielle"},
#       "low": {"color": "green", "priority": 2, "description": "Information"},
#       "info": {"color": "blue", "priority": 1, "description": "Simple information"},
#   }
#
#   LOG_TYPES = {
#       "authentication": ["login", "logout", "failed_login", "password_change", "mfa"],
#       "network": ["connection", "dns", "dhcp", "firewall", "proxy", "vpn"],
#       "system": ["process", "service", "file", "registry", "scheduled_task"],
#       "application": ["web", "database", "email", "api"],
#       "security": ["antivirus", "ids_ips", "waf", "dlp"],
#   }
#
#   SEVERITY_LEVELS = ["debug", "info", "notice", "warning", "error", "critical", "alert", "emergency"]
#
#   SOURCE_TYPES = {
#       "syslog": {"port": 514, "protocol": "udp"},
#       "windows_event": {"port": 5985, "protocol": "http"},
#       "netflow": {"port": 2055, "protocol": "udp"},
#       "json_api": {"port": 443, "protocol": "https"},
#   }
#
#   def get_criticity_priority(criticity: str) -> int:
#       """Retourne la priorité numérique d'une criticité."""
#       return CRITICITY_TAGS.get(criticity, {}).get("priority", 0)
