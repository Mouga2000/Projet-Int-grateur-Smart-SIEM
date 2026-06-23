# app/main.py
# -------------------------------
# Point d'entrée de l'application FastAPI
#
# Ce que tu dois mettre ici :
#
#   from fastapi import FastAPI
#   from app.core.config import settings
#   from app.core.database import engine, async_session
#   from app.api.v1.router import api_router
#   from app.api.middleware import setup_middlewares
#
#   app = FastAPI(
#       title=settings.APP_NAME,
#       version=settings.APP_VERSION,
#       docs_url="/docs" if settings.APP_ENV != "production" else None,
#   )
#
#   # Middlewares (CORS, TrustedHost, RateLimiting, etc.)
#   setup_middlewares(app)
#
#   # Routers
#   app.include_router(api_router, prefix="/api/v1")
#
#   @app.on_event("startup")
#   async def startup():
#       # Initialiser les connexions (DB, ES, Redis)
#       pass
#
#   @app.on_event("shutdown")
#   async def shutdown():
#       # Fermer les connexions
#       pass
#
#   @app.get("/")
#   async def root():
#       return {"message": "Smart SIEM API", "version": settings.APP_VERSION}
#
# Point d'entrée uvicorn : uvicorn app.main:app --reload
