#!/usr/bin/env python3
"""Test d'envoi d'email avec le template HTML."""

import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(_PROJECT_ROOT)
sys.path.insert(0, _PROJECT_ROOT)

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings
from app.services.email_templating import render_alert_email

if not settings.SMTP_HOST:
    print("SMTP non configure dans .env")
    sys.exit(1)

TO = settings.SMTP_USER

# Donnees simulees d'une alerte pour le template
fake_alert = {
    "title": "[TEST] Brute Force détectée",
    "rule_name": "Brute Force - 5 echecs auth en 60s",
    "severity": "critical",
    "source_ip": "192.168.1.100",
    "host": "server-01",
    "event_type": "auth",
    "description": "Tentative de brute force detectee sur le serveur Active Directory",
    "timestamp": "2026-06-29T10:30:00Z",
    "mitre_tactic": "credential_access",
    "mitre_technique": "T1110",
}

subject = f"[{fake_alert['severity'].upper()}] {fake_alert['title']}"

# Construction du message multipart (HTML + texte)
msg = MIMEMultipart("alternative")
msg["Subject"] = subject
msg["From"] = settings.SMTP_FROM
msg["To"] = TO

# Partie texte (fallback)
text_body = (
    f"{subject}\n{'=' * len(subject)}\n"
    f"Severite : {fake_alert['severity']}\n"
    f"Regle    : {fake_alert['rule_name']}\n"
    f"IP       : {fake_alert['source_ip']}\n"
    f"Hote     : {fake_alert['host']}\n"
    f"Type     : {fake_alert['event_type']}\n"
    f"MITRE    : {fake_alert['mitre_tactic']} / {fake_alert['mitre_technique']}\n"
    f"\n{fake_alert['description']}"
)
msg.attach(MIMEText(text_body, "plain", "utf-8"))

# Partie HTML (template)
html_body = render_alert_email(fake_alert)
msg.attach(MIMEText(html_body, "html", "utf-8"))

# Envoi
try:
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT or 587) as server:
        server.set_debuglevel(1)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD or "")
        server.send_message(msg)
    print(f"\nEmail envoye avec succes a {TO} (format HTML + texte)")
except Exception as e:
    print(f"\nErreur SMTP : {e}")
