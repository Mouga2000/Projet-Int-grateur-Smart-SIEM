# app/api/v1/router.py
# -------------------------------
# Regroupement de tous les routeurs v1

from fastapi import APIRouter

from app.api.v1 import (
    admin,
    alerts,
    archive,
    audit,
    auth,
    incidents,
    investigations,
    logs,
    mitre,
    notifications,
    playbooks,
    rules,
    ueba,
    users,
)

# from app.api.v1 import search, alerts, playbooks, reports, health

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(logs.router)
api_router.include_router(rules.router)
api_router.include_router(admin.router)
api_router.include_router(incidents.router)
api_router.include_router(alerts.router)
api_router.include_router(investigations.router)
api_router.include_router(notifications.router)
api_router.include_router(playbooks.router)
api_router.include_router(archive.router)
api_router.include_router(audit.router)
api_router.include_router(mitre.router)
api_router.include_router(ueba.router)
# api_router.include_router(health.router, prefix="/health", tags=["Health"])
# api_router.include_router(search.router, prefix="/search", tags=["Search"])
# api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
# api_router.include_router(playbooks.router, prefix="/playbooks", tags=["Playbooks"])
# api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
