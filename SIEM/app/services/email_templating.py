# app/services/email_templating.py
# -------------------------------
# Rendu des templates d'email HTML (sans dépendance externe)
# Utilise string.Template de la bibliotheque standard

import os
from string import Template
from typing import Optional


_TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "templates",
    "email",
)


def _load_template(name: str) -> Optional[str]:
    """Charge un fichier template depuis app/templates/email/."""
    path = os.path.join(_TEMPLATES_DIR, name)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# Cache des templates charges
_template_cache: dict[str, Template] = {}


def render_alert_email(alert: dict) -> str:
    """
    Rend le template HTML d'alerte avec les donnees de l'alerte.

    Retourne le corps HTML complet, ou une version texte simple
    si le template est introuvable.
    """
    if "alert_notification" not in _template_cache:
        raw = _load_template("alert_notification.html")
        if raw is None:
            # Fallback : message texte si pas de template
            return _fallback_text(alert)
        _template_cache["alert_notification"] = Template(raw)

    severity = (alert.get("severity") or "info").lower()
    tactic = alert.get("mitre_tactic") or ""
    technique = alert.get("mitre_technique") or ""

    # Section MITRE (optionnelle)
    mitre_section = ""
    if tactic or technique:
        mitre_section = f"""
            <div class="field">
                <div class="field-label">MITRE ATT&CK</div>
                <div>
                    <span class="mitre-tag">{tactic}</span>
                    <span class="mitre-tag">{technique}</span>
                </div>
            </div>
        """

    return _template_cache["alert_notification"].safe_substitute(
        title=_html_escape(alert.get("title") or alert.get("rule_name") or "Alerte SIEM"),
        severity=severity.upper(),
        severity_class=severity,
        timestamp=_html_escape(str(alert.get("timestamp") or "")),
        rule_name=_html_escape(str(alert.get("rule_name") or "N/A")),
        description=_html_escape(str(alert.get("description") or "Aucune description")),
        source_ip=_html_escape(str(alert.get("source_ip") or "N/A")),
        host=_html_escape(str(alert.get("host") or "N/A")),
        event_type=_html_escape(str(alert.get("event_type") or "N/A")),
        mitre_section=mitre_section,
        dashboard_url="http://localhost:8000",
    )


def _fallback_text(alert: dict) -> str:
    """Version texte simple si le template HTML est indisponible."""
    return (
        f"ALERTE SECURITE - {alert.get('title', 'Smart SIEM')}\n"
        f"{'=' * 50}\n"
        f"Severite : {alert.get('severity', 'N/A')}\n"
        f"Regle    : {alert.get('rule_name', 'N/A')}\n"
        f"IP       : {alert.get('source_ip', 'N/A')}\n"
        f"Hote     : {alert.get('host', 'N/A')}\n"
        f"Type     : {alert.get('event_type', 'N/A')}\n"
        f"MITRE    : {alert.get('mitre_tactic', 'N/A')} / {alert.get('mitre_technique', 'N/A')}\n"
        f"\n{alert.get('description', '')}"
    )


def _html_escape(text: str) -> str:
    """Echappe les caracteres HTML."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )
