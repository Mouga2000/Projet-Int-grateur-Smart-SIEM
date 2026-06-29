#!/usr/bin/env python3
"""
Évalue les performances du modèle UEBA après entraînement.

Analyse :
  1. Distribution des scores de risque (0-100) sur tous les profils
  2. Nombre d'utilisateurs "anormaux" (score > 70)
  3. Features contributives (moyennes des normaux vs anormaux)
  4. Test avec des données normales vs anormales simulées

Utilisation :
    python scripts/evaluate_ueba.py
"""

import asyncio
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import async_session_factory
from app.models.sql_models import ProfilUEBA
from app.services.ueba import (
    FEATURE_NAMES,
    compute_risk_score,
    extract_features,
    features_to_vector,
)


async def main():
    print("=" * 60)
    print("  EVALUATION DU MODELE UEBA")
    print("=" * 60)
    print()

    # 1. Charger le modèle
    model_path = "models/ueba/isolation_forest.joblib"
    if not os.path.exists(model_path):
        print(f"Modele introuvable : {model_path}")
        print("Lance d'abord : python scripts/train_ueba.py")
        return

    import joblib
    import numpy as np

    model = joblib.load(model_path)
    print(f"Modele : {model_path}")
    print()

    # 2. Récupérer tous les profils
    async with async_session_factory() as db:
        result = await db.execute(
            select(ProfilUEBA).order_by(ProfilUEBA.risk_score.desc())
        )
        profiles = result.scalars().all()

    if not profiles:
        print("Aucun profil UEBA trouve. Entraine d'abord le modele.")
        return

    print(f"Profils  : {len(profiles)} entites")
    print()

    # 3. Distribution des scores
    scores = [p.risk_score for p in profiles]
    buckets = {"0": 0, "1-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}

    for s in scores:
        if s == 0:
            buckets["0"] += 1
        elif s <= 20:
            buckets["1-20"] += 1
        elif s <= 40:
            buckets["21-40"] += 1
        elif s <= 60:
            buckets["41-60"] += 1
        elif s <= 80:
            buckets["61-80"] += 1
        else:
            buckets["81-100"] += 1

    print("Distribution des scores :")
    print(f"  {'Score':<12} {'Nombre':<8} {'%':<8}")
    print(f"  {'-'*28}")
    for bucket, count in buckets.items():
        pct = count / len(scores) * 100 if scores else 0
        bar = "#" * int(pct / 2)
        print(f"  {bucket:<12} {count:<8} {pct:.1f}%  {bar}")

    print()

    # 4. Statistiques
    seuil_alerte = 70
    anormaux = [p for p in profiles if p.risk_score >= seuil_alerte]
    print(f"Statistiques :")
    print(f"  Score moyen          : {sum(scores)/len(scores):.1f}")
    print(f"  Score median         : {sorted(scores)[len(scores)//2]}")
    print(f"  Score max            : {max(scores)}")
    print(f"  Score min            : {min(scores)}")
    print(f"  Anormaux (score>{seuil_alerte}) : {len(anormaux)}/{len(profiles)} ({len(anormaux)/len(profiles)*100:.1f}%)")
    print()

    # 5. Top 10 des entités les plus risquées
    print("Top 10 des entites les plus risquees :")
    print(f"  {'Entite':<55} {'Score':<8} {'Type':<10}")
    print(f"  {'-'*75}")
    for p in profiles[:10]:
        print(f"  {p.entity_id:<55} {p.risk_score:<8} {p.entity_type:<10}")
    print()

    # 6. Comparaison des features : normaux vs anormaux
    normaux_profiles = [p for p in profiles if p.risk_score < seuil_alerte]
    anormaux_profiles = anormaux

    if normaux_profiles and anormaux_profiles:
        print("Comparaison des features (moyennes) :")
        print(f"  {'Feature':<20} {'Normaux':<12} {'Anormaux':<12} {'Ecart':<12}")
        print(f"  {'-'*56}")

        def avg_feature(profiles_list, feat_name):
            vals = []
            for p in profiles_list:
                if isinstance(p.baseline, dict) and p.baseline.get(feat_name) is not None:
                    vals.append(p.baseline[feat_name])
            return sum(vals) / len(vals) if vals else 0

        for feat in FEATURE_NAMES:
            avg_norm = avg_feature(normaux_profiles[:100], feat)  # échantillon
            avg_anom = avg_feature(anormaux_profiles, feat)
            ecart = avg_anom - avg_norm
            print(f"  {feat:<20} {avg_norm:<12.3f} {avg_anom:<12.3f} {ecart:<12.3f}")
    print()

    # 7. Test avec des données synthétiques
    print("Test avec comportements simules :")
    print()

    # Comportement normal (bureau, jour, même IP)
    normal_events = [
        {"timestamp": "2026-06-29T09:00:00Z", "source_ip": "192.168.1.10", "log_type": "auth", "severity": "info", "decoded": {"user": "test_user"}},
        {"timestamp": "2026-06-29T10:00:00Z", "source_ip": "192.168.1.10", "log_type": "auth", "severity": "info", "decoded": {"user": "test_user"}},
        {"timestamp": "2026-06-29T11:00:00Z", "source_ip": "192.168.1.10", "log_type": "reseau", "severity": "info", "decoded": {"user": "test_user"}},
        {"timestamp": "2026-06-29T14:00:00Z", "source_ip": "192.168.1.10", "log_type": "auth", "severity": "info", "decoded": {"user": "test_user"}},
        {"timestamp": "2026-06-29T15:00:00Z", "source_ip": "192.168.1.10", "log_type": "systeme", "severity": "info", "decoded": {"user": "test_user"}},
    ]
    # Comportement anormal (3h du mat, 5 IPs différentes, 100% d'erreurs)
    anormal_events = [
        {"timestamp": "2026-06-29T03:15:00Z", "source_ip": f"10.0.0.{i}", "log_type": "auth", "severity": "error", "decoded": {"user": "attacker"}}
        for i in range(1, 6)
    ] * 3

    feats_norm = extract_features(normal_events)
    feats_anom = extract_features(anormal_events)
    score_norm = compute_risk_score(feats_norm)
    score_anom = compute_risk_score(feats_anom)

    print(f"  Comportement normal    : score = {score_norm}")
    print(f"  Comportement anormal   : score = {score_anom}")
    print()

    # Prédiction du modèle sur les deux cas
    vec_norm = np.array([features_to_vector(feats_norm)])
    vec_anom = np.array([features_to_vector(feats_anom)])
    pred_norm = model.predict(vec_norm)[0]  # 1 = normal
    pred_anom = model.predict(vec_anom)[0]  # -1 = anomalie

    print(f"  Prediction modele normal  : {'NORMAL' if pred_norm == 1 else 'ANOMALIE'}")
    print(f"  Prediction modele anormal : {'NORMAL' if pred_anom == 1 else 'ANOMALIE'}")

    ok = score_norm < 30 and score_anom > 60
    print()
    print(f"  Verification : {'OK' if ok else 'A REVOIR'}")
    print(f"    (normal < 30 et anormal > 60)")

    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
