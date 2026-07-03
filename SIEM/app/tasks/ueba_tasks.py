# app/tasks/ueba_tasks.py
# -------------------------------
# Tâches Celery pour l'analyse comportementale UEBA
#
# - train_anomaly_model : entraînement du modèle Isolation Forest
# - score_single_event  : scoring temps réel après ingestion d'un log
#
# Planification (Celery Beat) :
#   train_anomaly_model → tous les lundis à 2h
#   Utilise tout l'historique (pas de limite de jours)

import asyncio
from collections import defaultdict

from app.core.config import settings
from app.core.database import async_session_factory
from app.core.elasticsearch import get_es as get_es_client
from app.repositories.log_repo import LogRepository
from app.services import ueba as ueba_service
from app.tasks.celery import celery_app


@celery_app.task(bind=True, max_retries=2, soft_time_limit=3600)
def train_anomaly_model(self, days: int = None, index: str = None):
    """
    Entraîne le modèle UEBA sur tout l'historique disponible.

    - Par défaut (Celery Beat) : tous les logs (match_all)
    - Pour un entraînement sur période spécifique : days=30
    - Pour CLUE-LDS uniquement : days=3650, index='logs-clue'

    Déclenchement :
        celery -A app.tasks.celery call app.tasks.ueba_tasks.train_anomaly_model
    """

    async def _run():
        es = await get_es_client()
        repo = LogRepository(es)

        # Déterminer la requête : tout l'historique par défaut
        if days and days > 0:
            from datetime import datetime, timezone, timedelta
            date_from = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            query = {"range": {"timestamp": {"gte": date_from}}}
        else:
            query = {"match_all": {}}

        target_index = index or settings.ELASTICSEARCH_INDEX_LOGS

        # Utiliser scroll pour charger tous les résultats
        raw_es = es  # ElasticsearchClient renvoie l'instance AsyncElasticsearch
        resp = await raw_es.search(
            index=target_index,
            body={"query": query, "size": 5000, "sort": ["_doc"]},
            scroll="10m",
        )
        scroll_id = resp["_scroll_id"]
        hits = resp["hits"]["hits"]
        total = resp["hits"]["total"]["value"]

        # Grouper par entité
        groups = defaultdict(list)
        processed = 0

        while hits:
            for hit in hits:
                e = hit["_source"]
                entity_id = (
                    e.get("decoded", {}).get("user")
                    or e.get("raw_data", {}).get("uid")
                    or e.get("source_ip", "unknown")
                )
                groups[entity_id].append(e)

            processed += len(hits)
            if processed % 100000 == 0:
                print(f"[UEBA]  {processed}/{total} evenements, {len(groups)} utilisateurs")

            resp = await raw_es.scroll(scroll_id=scroll_id, scroll="10m")
            scroll_id = resp["_scroll_id"]
            hits = resp["hits"]["hits"]

        await raw_es.clear_scroll(scroll_id=scroll_id)

        print(f"[UEBA] Charge : {processed}/{total} evenements, {len(groups)} utilisateurs")

        if not groups:
            return {"status": "skipped", "reason": "Aucun evenement trouve"}

        # Entraîner le modèle
        print(f"[UEBA] Entrainement Isolation Forest...")
        async with async_session_factory() as db:
            result = await ueba_service.train_model(dict(groups), db)
            await db.commit()
            result["events_analyzed"] = processed
            result["entities_found"] = len(groups)
            print(f"[UEBA] Resultat : {result}")
            return result

    return asyncio.run(_run())


@celery_app.task(bind=True, max_retries=1, soft_time_limit=30)
def score_single_event(self, event: dict):
    """
    Calcule le score de risque UEBA pour un événement en temps réel.
    """

    async def _run():
        entity_id = (
            event.get("decoded", {}).get("user")
            or event.get("raw_data", {}).get("uid")
            or event.get("source_ip", "unknown")
        )

        async with async_session_factory() as db:
            score = await ueba_service.score_event(entity_id, event, db)
            await db.commit()
            return {"entity_id": entity_id, "risk_score": score}

    return asyncio.run(_run())
