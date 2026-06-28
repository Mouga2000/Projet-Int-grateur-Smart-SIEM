# app/models/sql_models.py
# -------------------------------
# Modèles SQLAlchemy pour PostgreSQL (données structurées)
#
# PostgreSQL stocke : utilisateurs, règles, playbooks, alertes, incidents, audits,
# notifications, profils UEBA
# Elasticsearch conserve : logs (données volumineuses / non structurées)

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base déclarative pour tous les modèles SQLAlchemy."""


# =============================================================================
# MIXINS
# =============================================================================


class TimestampMixin:
    """Ajoute created_at et updated_at automatiques."""

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class SoftDeleteMixin:
    """Ajoute le soft-delete."""

    deleted_at = Column(DateTime(timezone=True), nullable=True, default=None)


# =============================================================================
# USER
# =============================================================================


class User(Base, TimestampMixin, SoftDeleteMixin):
    """Utilisateur de la plateforme SIEM."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    mfa_secret = Column(String(64), nullable=True)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    role = Column(
        String(50), default="lecteur", nullable=False
    )  # lecteur, analyste, auditeur, rssi, administrateur
    perimeter = Column(
        JSON, default=list, nullable=False
    )  # ["equipe", "service", "filiale", "environnement"]
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# =============================================================================
# RULE (règle de corrélation)
# =============================================================================


class Rule(Base, TimestampMixin, SoftDeleteMixin):
    """Règle de corrélation / détection d'événements."""

    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    rule_type = Column(String(50), default="single_event", nullable=False)
    # single_event, threshold, correlation, sequence, ueba, custom
    enabled = Column(Boolean, default=True, nullable=False)
    severity = Column(
        String(20), default="medium", nullable=False
    )  # low, medium, high, critical
    mitre_tactic = Column(String(100), nullable=True)
    mitre_technique = Column(String(100), nullable=True)
    condition = Column(JSON, default=dict, nullable=False)
    actions = Column(JSON, default=dict, nullable=False)
    priority = Column(Integer, default=50, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_by = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<Rule {self.name} ({self.severity})>"


# =============================================================================
# PLAYBOOK (automatisation SOAR)
# =============================================================================


class Playbook(Base, TimestampMixin, SoftDeleteMixin):
    """Playbook d'automatisation SOAR."""

    __tablename__ = "playbooks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    trigger = Column(String(50), default="manual", nullable=False)
    # manual, alert_created, alert_escalated, scheduled, webhook
    enabled = Column(Boolean, default=True, nullable=False)
    steps = Column(JSON, default=list, nullable=False)
    variables = Column(JSON, default=dict, nullable=False)
    timeout_seconds = Column(Integer, default=300, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    last_executed_at = Column(DateTime(timezone=True), nullable=True)
    execution_count = Column(Integer, default=0, nullable=False)
    created_by = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<Playbook {self.name}>"


# =============================================================================
# INCIDENT (regroupement d'alertes)
# =============================================================================


class Incident(Base, TimestampMixin):
    """Incident de sécurité regroupant plusieurs alertes."""

    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cree_le = Column(
        "cree_le",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    statut = Column("statut", String(20), default="ouverte", nullable=False)
    # ouverte, en_cours, resolue, cloturee
    assigne_a = Column("assigne_a", Integer, ForeignKey("users.id"), nullable=True)
    alert_ids = Column(JSON, default=list, nullable=False)
    rule_ids = Column(JSON, default=list, nullable=False)
    mitre_attack_ids = Column(JSON, default=list, nullable=False)
    notes_resolution = Column("notes_resolution", Text, nullable=True)
    timeline = Column(JSON, default=list, nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    assignee = relationship("User", foreign_keys=[assigne_a])

    def __repr__(self):
        return f"<Incident #{self.id} [{self.statut}]>"


# =============================================================================
# ALERTE
# =============================================================================


class Alert(Base, TimestampMixin):
    """Alerte de sécurité déclenchée par une règle de corrélation."""

    __tablename__ = "alertes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cree_le = Column(
        "cree_le",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    regle_id = Column("regle_id", Integer, ForeignKey("rules.id"), nullable=True)
    niveau = Column(String(20), default="medium", nullable=False)
    titre = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    mitre = Column(JSON, default=dict, nullable=True)
    source_ip = Column(String(45), nullable=True)
    host = Column(String(255), nullable=True)
    statut = Column(String(20), default="ouverte", nullable=False)
    score_confiance = Column("score_confiance", Integer, default=50, nullable=False)

    regle = relationship("Rule", foreign_keys=[regle_id])

    def __repr__(self):
        return f"<Alert #{self.id} {self.titre} [{self.niveau}]>"


# =============================================================================
# PROFIL UEBA (analyse comportementale)
# =============================================================================


class ProfilUEBA(Base, TimestampMixin):
    """Profil comportemental d'une entité (utilisateur, machine)."""

    __tablename__ = "profils_ueba"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # user, host, process
    baseline = Column(JSON, default=dict, nullable=False)
    risk_score = Column("risk_score", Integer, default=0, nullable=False)
    last_updated = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):
        return f"<ProfilUEBA {self.entity_id} ({self.entity_type}) score={self.risk_score}>"


# =============================================================================
# AUDIT LOG (trace des actions sensibles)
# =============================================================================


class AuditLog(Base, TimestampMixin):
    """Trace d'une action sensible dans le SIEM."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    username = Column(String(100), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    # login, logout, mfa_verify, create_user, update_role, delete_user, rule_create, playbook_execute…
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(50), nullable=True)
    details = Column(JSON, default=dict, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    result = Column(String(20), default="success", nullable=False)  # success, failed

    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_audit_logs_user_action", "user_id", "action"),
        Index("ix_audit_logs_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.username} [{self.result}]>"


# =============================================================================
# NOTIFICATION
# =============================================================================


class Notification(Base, TimestampMixin):
    """Notification destinée à un utilisateur."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    channel = Column(String(20), default="in_app", nullable=False)
    # in_app, email, slack, sms
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    reference_type = Column(String(50), nullable=True)  # alert, incident, report
    reference_id = Column(String(50), nullable=True)
    delivered = Column(Boolean, default=False, nullable=False)
    delivered_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<Notification #{self.id} {self.title}>"


# =============================================================================
# ARCHIVE (logs archivés avec certification d'intégrité)
# =============================================================================


class Archive(Base, TimestampMixin):
    """Archive de logs conforme (intégrité + horodatage)."""

    __tablename__ = "archives"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_from = Column(DateTime(timezone=True), nullable=False)
    date_to = Column(DateTime(timezone=True), nullable=False)
    log_count = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)

    # Intégrité cryptographique
    sha256_hash = Column(String(64), nullable=False)
    merkle_root = Column(String(64), nullable=False)

    # Chaîne de confiance (chaque archive hashée pointe vers la précédente)
    previous_archive_id = Column(Integer, ForeignKey("archives.id"), nullable=True)
    previous_hash = Column(String(64), nullable=True)
    chain_hash = Column(String(64), nullable=False)

    # Horodatage certifié
    timestamp_signature = Column(Text, nullable=True)
    certified_by = Column(String(100), default="self")
    certified_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Cycle de vie
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="active")

    # Relations
    previous_archive = relationship(
        "Archive", remote_side=[id], foreign_keys=[previous_archive_id]
    )

    def __repr__(self):
        return f"<Archive #{self.id} [{self.date_from.date()} → {self.date_to.date()}] ({self.log_count} logs)>"


# =============================================================================
# INVESTIGATION (regroupement de logs suspects pour enquete croisee)
# =============================================================================


class InvestigationLog(Base, TimestampMixin):
    """Lien entre une investigation et un log, avec note d'analyse."""

    __tablename__ = "investigation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), nullable=False)
    log_id = Column(String(100), nullable=False, index=True)
    log_index = Column(String(100), nullable=True)
    analyst_note = Column(Text, nullable=True)
    analyst_verdict = Column(String(20), default="suspect")
    added_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    investigation = relationship("Investigation", foreign_keys=[investigation_id])

    def __repr__(self):
        return (
            f"<InvestigationLog #{self.id} log={self.log_id} [{self.analyst_verdict}]>"
        )


class Investigation(Base, TimestampMixin):
    """Regroupement de logs suspects pour investigation croisee."""

    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="ouverte", nullable=False)
    severity = Column(String(20), default="medium", nullable=False)
    tags = Column(JSON, default=list, nullable=False)
    log_ids = Column(JSON, default=list, nullable=False)
    mitre_tactic = Column(String(100), nullable=True)
    mitre_technique = Column(String(100), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    assignee = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Investigation #{self.id} '{self.title}' [{self.status}]>"
