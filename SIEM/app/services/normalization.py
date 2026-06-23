# app/services/normalization.py
# -------------------------------
# Service de normalisation des logs
#
# Ce que tu dois mettre ici :
#
#   # Ce service transforme les logs bruts (Syslog, Windows Event, NetFlow, JSON, etc.)
#   # en un format normalisé commun pour le stockage dans Elasticsearch.
#
#   class NormalizationService:
#       """Normalise les logs de différents formats vers un schéma commun."""
#
#       SUPPORTED_FORMATS = ["syslog", "windows_event", "netflow", "json", "cef", "leef"]
#
#       async def normalize(self, raw_log: dict | str, source_type: str) -> dict:
#           """Détecte le format et normalise le log."""
#           pass
#
#       async def parse_syslog(self, raw: str) -> dict:
#           """Parse un message Syslog (RFC 3164 / RFC 5424)."""
#           pass
#
#       async def parse_windows_event(self, raw: dict) -> dict:
#           """Transforme un événement Windows XML/JSON en format commun."""
#           pass
#
#       async def parse_cef(self, raw: str) -> dict:
#           """Parse un format CEF (Common Event Format) - ArcSight."""
#           pass
#
#       async def parse_leef(self, raw: str) -> dict:
#           """Parse un format LEEF (Log Event Extended Format) - QRadar/IBM."""
#           pass
#
#       async def enrich_log(self, normalized: dict) -> dict:
#           """Enrichit le log avec des données contextuelles (geoip, whois, etc.)."""
#           pass
