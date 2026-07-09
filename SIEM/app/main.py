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

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


from app.api.v1.router import api_router
from app.core.database import close_db, init_db
from app.core.redis import close_redis, get_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application."""
    # Au démarrage : créer les tables PostgreSQL si elles n'existent pas
    await init_db()
    await get_redis()  # Initialiser Redis
    yield
    # À l'arrêt : fermer les connexions
    await close_db()
    await close_redis()
    from app.core.elasticsearch import close_es as close_elasticsearch
    await close_elasticsearch()


app = FastAPI(
    title="Smart SIEM API",
    description="API du système de gestion des événements de sécurité",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# --- Middleware : forcer HTTPS sur les Location header (pour les redirects) ---
@app.middleware("http")
async def upgrade_location_to_https(request: Request, call_next):
    response = await call_next(request)
    if response.status_code in (301, 302, 303, 307, 308) and response.headers.get("location", "").startswith("http://"):
        response.headers["location"] = response.headers["location"].replace("http://", "https://", 1)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "https://projet-int-grateur-smart-siem.vercel.app",          # Frontend Vercel
        "https://api.smart-siem.strife-cyber.com",                    # API via Traefik
        "https://api.smart-siem.strife-cyber.org",                    # API (org)
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
