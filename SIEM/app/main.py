# app/main.py
# -------------------------------
# Point d'entrée de l'application FastAPI
#
# Ce que tu dois mettre ici :
#
#   from fastapi import FastAPI
#   from app.core.config import settings
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
#       # Initialiser les connexions (ES, Redis)
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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1.router import api_router
from app.core.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application."""
    # Au démarrage : créer les tables PostgreSQL si elles n'existent pas
    await init_db()
    yield
    # À l'arrêt : fermer les connexions
    await close_db()


app = FastAPI(
    title="Smart SIEM API",
    description="API du système de gestion des événements de sécurité",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routeurs
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Smart SIEM API is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}