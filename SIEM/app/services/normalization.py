# app/services/normalization.py
# -------------------------------
# Service de normalisation des logs

import re
from typing import Optional

class NormalizationService:
    """Normalise les logs bruts en format structuré avec tagging et enrichissement."""

    # Règles de tagging automatique basées sur le contenu du message
    SEVERITY_RULES = [
        (r"(?i)(failed password|invalid user|authentication failure|brute force)", "critical", "auth"),
        (r"(?i)(error|timeout|exception|traceback|failed)", "error", None),
        (r"(?i)(refused|denied|blocked|forbidden|unauthorized)", "warning", "auth"),
        (r"(?i)(warning|warn|threshold|limit)", "warning", None),
        (r"(?i)(login|logout|authenticated|session)", "info", "auth"),
        (r"(?i)(connected|disconnected|link|interface|port)", "info", "reseau"),
        (r"(?i)(started|stopped|restarted|service|process)", "info", "systeme"),
    ]

    @staticmethod
    def auto_tag(message: str, current_severity: Optional[str] = None) -> dict:
        """
        Analyse le message pour déterminer la criticité et le type de log.

        Retourne {"severity": str, "log_type": str, "tags": list}
        """
        result = {
            "severity": current_severity or "info",
            "log_type": "application",
            "tags": [],
        }

        for pattern, severity, log_type in NormalizationService.SEVERITY_RULES:
            if re.search(pattern, message):
                if severity != "info" or result["severity"] == "info":
                    result["severity"] = severity
                if log_type:
                    result["log_type"] = log_type
                break

        # Tags automatiques
        result["tags"].append(result["severity"])
        result["tags"].append(result["log_type"])

        # Tags additionnels selon la source
        if re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", message):
            result["tags"].append("ip_mentioned")

        return result

    @staticmethod
    def extract_structured(message: str) -> dict:
        """
        Extrait des données structurées du message brut.
        Retourne un dict avec les champs identifiés (IP, MAC, user, port, etc.).
        """
        decoded = {}

        # Extraire les IPs
        ips = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", message)
        if ips:
            decoded["ips"] = ips

        # Extraire les adresses MAC (XX:XX:XX:XX:XX:XX ou XX-XX-XX-XX-XX-XX)
        macs = re.findall(
            r"(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})",
            message
        )
        if macs:
            decoded["macs"] = macs

        # Extraire les noms d'utilisateur (pattern: user=XXX ou 'user 'XXX)
        user_match = re.search(r"(?:user|username)[=:']\s*(\S+)", message, re.IGNORECASE)
        if user_match:
            decoded["user"] = user_match.group(1)

        # Extraire les ports
        ports = re.findall(r"(?:port\s+)(\d+)", message, re.IGNORECASE)
        if ports:
            decoded["ports"] = [int(p) for p in ports]

        return decoded

    @staticmethod
    async def normalize(log_data: dict) -> dict:
        """
        Pipeline tolérant : accepte les champs manquants et les formats variés.
        Gère à la fois le format SIEM (source_ip, host, raw_message) et
        le format Agent (hostname, event_type, message).
        """
        # --- Message brut ---
        raw_message = log_data.get("raw_message") or log_data.get("message") or ""

        # --- Horodatage ---
        raw_ts = log_data.get("timestamp")
        if raw_ts is None:
            from datetime import datetime, timezone
            raw_ts = datetime.now(timezone.utc)

        # --- Tagging automatique (criticité, type) ---
        tags_info = NormalizationService.auto_tag(raw_message, log_data.get("severity"))
        severity = tags_info["severity"]
        log_type = tags_info["log_type"]
        tags = tags_info["tags"]

        # --- Enrichissement ---
        decoded = NormalizationService.extract_structured(raw_message)

        # --- Mapping des champs agent → SIEM ---
        # Si l'agent a fourni event_type, on l'utilise (surclasse le tagging auto)
        if log_data.get("event_type"):
            log_type = log_data["event_type"]

        # Si l'agent a fourni hostname, on l'utilise comme host
        host = log_data.get("host") or log_data.get("hostname") or "unknown"

        # Si l'agent a fourni source_ip ou hostname comme source
        source_ip = log_data.get("source_ip") or log_data.get("src_ip") or host or "0.0.0.0"

        # --- Données supplémentaires de l'agent (préservées dans raw_data) ---
        raw_data = {}
        for key in ["agent_id", "operating_system", "collector", "event_id"]:
            if log_data.get(key):
                raw_data[key] = log_data[key]
        if log_data.get("data"):
            raw_data["data"] = log_data["data"]

        # --- Assemblage du document normalisé ---
        normalized = {
            "timestamp": raw_ts.isoformat() if hasattr(raw_ts, "isoformat") else str(raw_ts),
            "source_ip": source_ip,
            "host": host,
            "log_type": log_type,
            "severity": severity,
            "raw_message": raw_message,
            "tags": tags,
            "decoded": decoded if decoded else None,
            "raw_data": raw_data if raw_data else None,
        }

        # Nettoyer les champs None
        return {k: v for k, v in normalized.items() if v is not None}
