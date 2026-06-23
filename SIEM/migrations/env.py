# migrations/env.py
# -------------------------------
# Configuration Alembic pour les migrations de base de données
#
# Ce que tu dois mettre ici :
#
#   from logging.config import fileConfig
#   from sqlalchemy import engine_from_config, pool
#   from alembic import context
#
#   # Import de la base déclarative pour l'autogenerate
#   from app.models.base import Base
#   from app.core.config import settings
#
#   # Importer tous les modèles pour que Base.metadata les connaisse
#   import app.models.user
#   import app.models.alert
#   import app.models.rule
#   import app.models.playbook
#   import app.models.incident
#   import app.models.notification
#   import app.models.audit_log
#   import app.models.log
#
#   config = context.config
#   config.set_main_option("sqlalchemy.url", settings.DATABASE_SYNC_URL)
#
#   if config.config_file_name is not None:
#       fileConfig(config.config_file_name)
#
#   target_metadata = Base.metadata
#
#   def run_migrations_offline():
#       """Exécute les migrations en mode offline."""
#       context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata)
#       with context.begin_transaction():
#           context.run_migrations()
#
#   def run_migrations_online():
#       """Exécute les migrations en mode online."""
#       connectable = engine_from_config(
#           config.get_section(config.config_ini_section, {}),
#           prefix="sqlalchemy.",
#           poolclass=pool.NullPool,
#       )
#       with connectable.connect() as connection:
#           context.configure(connection=connection, target_metadata=target_metadata)
#           with context.begin_transaction():
#               context.run_migrations()
#
#   if context.is_offline_mode():
#       run_migrations_offline()
#   else:
#       run_migrations_online()
