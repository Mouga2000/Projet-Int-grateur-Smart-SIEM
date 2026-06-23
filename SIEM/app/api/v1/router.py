# app/api/v1/router.py
# -------------------------------
# Regroupement de tous les routeurs v1
#
# Ce que tu dois mettre ici :
#
#   from fastapi import APIRouter
#   from app.api.v1 import logs, search, alerts, playbooks, auth, users, reports, health
#
#   api_router = APIRouter()
#
#   api_router.include_router(health.router, prefix="/health", tags=["health"])
#   api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
#   api_router.include_router(users.router, prefix="/users", tags=["users"])
#   api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
#   api_router.include_router(search.router, prefix="/search", tags=["search"])
#   api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
#   api_router.include_router(playbooks.router, prefix="/playbooks", tags=["playbooks"])
#   api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
