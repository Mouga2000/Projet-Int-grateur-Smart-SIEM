# app/utils/logging.py
# -------------------------------
# Configuration de Loguru (logging structuré)
#
# Ce que tu dois mettre ici :
#
#   import sys
#   from loguru import logger
#   from app.core.config import settings
#
#   # Configuration du logger
#   logger.remove()  # Supprime le handler par défaut
#
#   # Format console (développement)
#   logger.add(
#       sys.stderr,
#       format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
#       level=settings.LOG_LEVEL.upper(),
#       colorize=True,
#   )
#
#   # Format fichier (production) — rotation et rétention
#   logger.add(
#       "logs/siem_{time:YYYY-MM-DD}.log",
#       format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
#       level="INFO",
#       rotation="10 MB",
#       retention="30 days",
#       compression="gz",
#       enqueue=True,  # Thread-safe
#   )
#
#   # Export pour utilisation dans toute l'app
#   logger = logger
