# app/services/ueba.py
# -------------------------------
# Service d'analyse comportementale UEBA
#
# Features extraites des logs Elasticsearch → Isolation Forest → score de risque (0-100)
#
# Dépendances : scikit-learn, joblib, numpy

import os
import statistics
from datetime import datetime, timezone
from typing import List, Optional

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.sql_models import ProfilUEBA

# ---------------------------------------------------------------------------
# Noms des features dans l'ordre du vecteur
# ---------------------------------------------------------------------------
FEATURE_NAMES = [
    "mean_hour",
    "std_hour",
    "total_events",
    "unique_ips",
    "unique_users",
    "unique_log_types",
    "error_ratio",
    "critical_ratio",
    "avg_bytes",       # Volume moyen de données transférées par événement
]


# ============================================================================
# 1. FEATURE ENGINEERING
# ============================================================================


def extract_features(events: List[dict], max_events: int = 20000) -> dict:
    """
    Extrait les indicateurs comportementaux d'une liste d'événements normalisés.

    Args:
        events: Liste de logs provenant d'Elasticsearch (format normalisé SIEM).
        max_events: Nombre max d'événements à analyser par utilisateur
                    (au-delà, on échantillonne pour éviter les MemoryError).

    Returns:
        Dictionnaire de features (clés = FEATURE_NAMES + metadata).
    """
    if not events:
        return {}

    # Échantillonnage pour éviter les MemoryError sur les utilisateurs
    # très actifs (certains ont des millions d'événements)
    if len(events) > max_events:
        import random
        events = random.sample(events, max_events)

    # Temporalité : heures d'activité
    hours = []
    for e in events:
        ts = e.get("timestamp")
        if ts:
            try:
                ts_clean = ts.replace("Z", "+00:00") if isinstance(ts, str) else ts
                h = datetime.fromisoformat(str(ts_clean)).hour
                hours.append(h)
            except (ValueError, AttributeError, TypeError):
                pass

    mean_hour = statistics.mean(hours) if hours else 12.0
    std_hour = statistics.stdev(hours) if len(hours) > 1 else 2.0

    # Types de logs et sévérités
    log_types = [e.get("log_type", "unknown") for e in events]
    severities = [e.get("severity", "info") for e in events]
    sev_counts: dict = {}
    for s in severities:
        sev_counts[s] = sev_counts.get(s, 0) + 1

    total = max(len(events), 1)

    # IPs source distinctes
    source_ips = {e.get("source_ip") for e in events if e.get("source_ip")}

    # Utilisateurs distincts (decoded.user, ou raw_data.uid en fallback)
    users: set = set()
    for e in events:
        user = None
        decoded = e.get("decoded")
        if isinstance(decoded, dict) and decoded.get("user"):
            user = decoded["user"]
        if not user:
            raw_data = e.get("raw_data")
            if isinstance(raw_data, dict) and raw_data.get("uid"):
                user = raw_data["uid"]
        if user:
            users.add(str(user))

    # Volume de données transférées (bytes, size, ou raw_data.size)
    total_bytes = 0
    for e in events:
        b = e.get("bytes") or e.get("size") or 0
        if not b:
            rd = e.get("raw_data", {}) if isinstance(e.get("raw_data"), dict) else {}
            b = rd.get("bytes") or rd.get("size") or 0
        total_bytes += b
    avg_bytes = round(total_bytes / total, 2)

    return {
        # Features numériques pour Isolation Forest
        "mean_hour":        round(mean_hour, 2),
        "std_hour":         round(std_hour, 2),
        "total_events":     len(events),
        "unique_ips":       len(source_ips),
        "unique_users":     len(users),
        "unique_log_types": len(set(log_types)),
        "error_ratio":      round(sev_counts.get("error", 0) / total, 3),
        "critical_ratio":   round(sev_counts.get("critical", 0) / total, 3),
        "avg_bytes":        avg_bytes,
    }


def features_to_vector(features: dict) -> List[float]:
    """
    Convertit un dictionnaire de features en vecteur numérique ordonné
    (dans l'ordre de FEATURE_NAMES) pour Isolation Forest.
    """
    return [features.get(k, 0.0) for k in FEATURE_NAMES]


# ============================================================================
# 2. SCORING
# ============================================================================


def compute_risk_score(features: dict) -> int:
    """
    Calcule le score de risque (0-100) d'une entité.

    Combine :
    - Isolation Forest (détection d'anomalie non supervisée)
    - Règles métier (sur-score pour les cas évidents)
    """
    model_path = os.path.join(settings.UEBA_MODEL_PATH, "isolation_forest.joblib")

    if not os.path.exists(model_path):
        return 0  # Pas encore de modèle → risque inconnu

    try:
        model = joblib.load(model_path)
        vector = features_to_vector(features)
        prediction = model.predict([vector])[0]  # 1 = normal, -1 = anomalie
    except Exception:
        prediction = 1  # Erreur de chargement → considéré normal

    base_score = 60 if prediction == -1 else 10

    # Règles métier
    bonus = 0
    if features.get("error_ratio", 0) > 0.5:
        bonus += 15
    if features.get("critical_ratio", 0) > 0.1:
        bonus += 20
    if features.get("unique_ips", 0) > 20:
        bonus += 10
    if features.get("avg_bytes", 0) > 100000:   # > 100 Ko/événement → suspect
        bonus += 15
    if features.get("avg_bytes", 0) > 1000000:  # > 1 Mo/événement → très suspect
        bonus += 25

    return min(100, base_score + bonus)


# ============================================================================
# 3. PROFILS (CRUD)
# ============================================================================


async def get_profile(db: AsyncSession, entity_id: str) -> Optional[dict]:
    """
    Récupère le profil UEBA d'une entité.

    Args:
        db: Session SQLAlchemy.
        entity_id: Identifiant de l'entité (user ou IP).

    Returns:
        Dictionnaire du profil ou None si inexistant.
    """
    result = await db.execute(
        select(ProfilUEBA).where(ProfilUEBA.entity_id == entity_id)
    )
    profile = result.scalar_one_or_none()
    return _profile_to_dict(profile) if profile else None


async def update_profile(
    db: AsyncSession,
    entity_id: str,
    entity_type: str = "user",
    baseline: dict = None,
    risk_score: int = 0,
) -> dict:
    """
    Crée ou met à jour le profil UEBA d'une entité.
    """
    result = await db.execute(
        select(ProfilUEBA).where(ProfilUEBA.entity_id == entity_id)
    )
    profile = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)

    if profile:
        if baseline is not None:
            profile.baseline = baseline
        profile.risk_score = risk_score
        profile.last_updated = now
    else:
        profile = ProfilUEBA(
            entity_id=entity_id,
            entity_type=entity_type,
            baseline=baseline or {},
            risk_score=risk_score,
        )
        db.add(profile)

    await db.flush()
    await db.refresh(profile)
    return _profile_to_dict(profile)


def _profile_to_dict(profile: ProfilUEBA) -> dict:
    """Convertit un objet ProfilUEBA SQLAlchemy en dictionnaire sérialisable."""
    return {
        "id": profile.id,
        "entity_id": profile.entity_id,
        "entity_type": profile.entity_type,
        "baseline": profile.baseline,
        "risk_score": profile.risk_score,
        "last_updated": (
            profile.last_updated.isoformat() if profile.last_updated else None
        ),
    }


# ============================================================================
# 4. ENTRAÎNEMENT DU MODÈLE
# ============================================================================


async def train_model(events_by_entity: dict, db: AsyncSession) -> dict:
    """
    Entraîne un modèle Isolation Forest sur les profils d'entités.

    Args:
        events_by_entity: Dictionnaire {entity_id: [events...]}.
        db: Session SQLAlchemy pour mettre à jour les profils.

    Returns:
        Dictionnaire de résultat (status, entities, model).
    """
    os.makedirs(settings.UEBA_MODEL_PATH, exist_ok=True)

    # Construire la matrice X à partir des features
    X: List[List[float]] = []
    entity_ids: List[str] = []

    for entity_id, events in events_by_entity.items():
        feats = extract_features(events)
        if not feats:
            continue
        X.append(features_to_vector(feats))
        entity_ids.append(entity_id)

    if len(X) < 5:
        return {
            "status": "skipped",
            "reason": f"Pas assez d'entités ({len(X)} < 5) pour entraîner le modèle",
        }

    # Entraînement
    model = IsolationForest(
        contamination=0.1,
        random_state=42,
        n_estimators=100,
    )
    model.fit(np.array(X))

    # Sauvegarde
    model_path = os.path.join(settings.UEBA_MODEL_PATH, "isolation_forest.joblib")
    joblib.dump(model, model_path)

    # Mise à jour des profils en base
    updated = 0
    for entity_id, events in events_by_entity.items():
        feats = extract_features(events)
        if not feats:
            continue
        score = compute_risk_score(feats)

        result = await db.execute(
            select(ProfilUEBA).where(ProfilUEBA.entity_id == entity_id)
        )
        profile = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if profile:
            profile.baseline = feats
            profile.risk_score = score
            profile.last_updated = now
        else:
            profile = ProfilUEBA(
                entity_id=entity_id,
                entity_type="user",
                baseline=feats,
                risk_score=score,
            )
            db.add(profile)
        updated += 1

    await db.flush()

    return {
        "status": "success",
        "entities_trained": updated,
        "model_path": model_path,
    }


# ============================================================================
# 5. SCORING TEMPS RÉEL
# ============================================================================


async def score_event(entity_id: str, event: dict, db: AsyncSession) -> int:
    """
    Calcule et persist le score de risque pour un événement en temps réel.

    Args:
        entity_id: Identifiant de l'entité concernée.
        event: Log normalisé venant d'être ingéré.
        db: Session SQLAlchemy.

    Returns:
        Score de risque (0-100).
    """
    feats = extract_features([event])
    if not feats:
        return 0

    score = compute_risk_score(feats)

    # Mise à jour rapide du profil (dernier score seulement)
    result = await db.execute(
        select(ProfilUEBA).where(ProfilUEBA.entity_id == entity_id)
    )
    profile = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)

    if profile:
        profile.risk_score = score
        profile.last_updated = now
        await db.flush()

    return score
