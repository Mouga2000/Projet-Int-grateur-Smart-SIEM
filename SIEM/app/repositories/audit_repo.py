# app/repositories/audit_repo.py
# -------------------------------
# Repository pour AuditLog
#
# Ce que tu dois mettre ici :
#
#   from app.repositories.base import BaseRepository
#   from app.models.audit_log import AuditLog
#   from datetime import datetime
#   from typing import Optional
#
#   class AuditLogRepository(BaseRepository):
#       """CRUD pour les logs d'audit."""
#
#       def __init__(self, db):
#           super().__init__(db)
#           self.model = AuditLog
#
#       async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 50) -> list[AuditLog]:
#           pass
#
#       async def get_by_action(self, action: str, skip: int = 0, limit: int = 50) -> list[AuditLog]:
#           pass
#
#       async def get_by_date_range(self, date_from: datetime, date_to: datetime) -> list[AuditLog]:
#           pass
#
#       async def log_action(
#           self,
#           user_id: Optional[int],
#           action: str,
#           resource_type: Optional[str] = None,
#           resource_id: Optional[str] = None,
#           details: dict = None,
#           ip_address: Optional[str] = None,
#           success: bool = True,
#       ) -> AuditLog:
#           """Enregistre une action d'audit."""
#           pass


from elasticsearch import AsyncElasticsearch
from datetime import datetime
from app.core.config import settings
from typing import List

class AuditRepository:
    def __init__(self, es: AsyncElasticsearch):
        self.es = es
        self.index_prefix = settings.ELASTICSEARCH_INDEX_AUDIT
    
    def _get_index_name(self) -> str:
        """Retourne le nom de l'index pour le jour courant"""
        today = datetime.now().strftime("%Y-%m-%d")
        return f"{self.index_prefix}-{today}"
    
    async def log_action(self, audit_data: dict) -> dict:
        """Journalise une action utilisateur"""
        audit_data["timestamp"] = datetime.now().isoformat()
        
        # Ajouter les métadonnées de base
        if "user_id" not in audit_data:
            audit_data["user_id"] = "system"
        
        response = await self.es.index(
            index=self._get_index_name(),
            body=audit_data,
            refresh=True
        )
        audit_data["_id"] = response["_id"]
        return audit_data
    
    async def log_login_attempt(self, user_id: str, username: str, success: bool, ip_address: str = None):
        """Journalise une tentative de connexion"""
        return await self.log_action({
            "user_id": user_id,
            "username": username,
            "action": "login",
            "result": "success" if success else "failed",
            "ip_address": ip_address or "unknown",
            "details": {"method": "password"}
        })
    
    async def log_logout(self, user_id: str, username: str):
        """Journalise une déconnexion"""
        return await self.log_action({
            "user_id": user_id,
            "username": username,
            "action": "logout",
            "result": "success"
        })
    
    async def log_mfa_verification(self, user_id: str, username: str, success: bool):
        """Journalise une vérification MFA"""
        return await self.log_action({
            "user_id": user_id,
            "username": username,
            "action": "mfa_verify",
            "result": "success" if success else "failed",
            "details": {"method": "totp"}
        })
    
    async def log_user_management(self, user_id: str, action: str, target_username: str, details: dict = None):
        """Journalise une action de gestion utilisateur"""
        return await self.log_action({
            "user_id": user_id,
            "username": target_username,
            "action": action,  # create_user, update_role, delete_user, etc.
            "result": "success",
            "details": details or {}
        })
    
    async def get_audit_logs(self, filters: dict = None, limit: int = 100) -> List[dict]:
        """Récupère les logs d'audit avec filtres"""
        query = {
            "query": {
                "bool": {
                    "must": []
                }
            },
            "size": limit,
            "sort": [{"timestamp": {"order": "desc"}}]
        }
        
        if filters:
            for key, value in filters.items():
                query["query"]["bool"]["must"].append(
                    {"term": {key: value}}
                )
        
        response = await self.es.search(index=f"{self.index_prefix}-*", body=query)
        logs = []
        for hit in response["hits"]["hits"]:
            log = hit["_source"]
            log["_id"] = hit["_id"]
            logs.append(log)
        return logs