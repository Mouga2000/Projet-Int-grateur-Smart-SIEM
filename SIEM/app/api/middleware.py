# app/api/middleware.py
# -------------------------------
# Middlewares FastAPI (logging, auth, rate limiting, CORS)
#
# Ce que tu dois mettre ici :
#
#   from fastapi import FastAPI, Request
#   from fastapi.middleware.cors import CORSMiddleware
#   from fastapi.middleware.trustedhost import TrustedHostMiddleware
#   from starlette.middleware.base import BaseHTTPMiddleware
#   import time
#   from app.core.config import settings
#   from app.utils.logging import logger
#
#   def setup_middlewares(app: FastAPI):
#       """Configure tous les middlewares."""
#
#       # CORS
#       app.add_middleware(
#           CORSMiddleware,
#           allow_origins=settings.CORS_ORIGINS.split(","),
#           allow_credentials=True,
#           allow_methods=["*"],
#           allow_headers=["*"],
#       )
#
#       # Trusted Hosts
#       app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
#
#       # Request/Response logging
#       @app.middleware("http")
#       async def log_requests(request: Request, call_next):
#           start = time.time()
#           response = await call_next(request)
#           duration = time.time() - start
#           logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration:.3f}s)")
#           return response
#
#   # Middleware optionnel : Rate Limiting
#   # class RateLimitMiddleware(BaseHTTPMiddleware):
#   #     async def dispatch(self, request, call_next):
#   #         # Implémenter un sliding window counter avec Redis
#   #         pass
#
#   # Middleware optionnel : Audit Trail
#   # class AuditMiddleware(BaseHTTPMiddleware):
#   #     async def dispatch(self, request, call_next):
#   #         # Logger chaque action sensible (DELETE, PUT, POST)
#   #         pass
