# app/repositories/user_repo.py
# -------------------------------
# Repository pour User
#
# Ce que tu dois mettre ici :
#
#   from app.repositories.base import BaseRepository
#   from app.models.user import User
#   from typing import Optional
#
#   class UserRepository(BaseRepository):
#       """CRUD pour les utilisateurs."""
#
#       def __init__(self, db):
#           super().__init__(db)
#           self.model = User
#
#       async def get_by_email(self, email: str) -> Optional[User]:
#           """Cherche un utilisateur par email."""
#           pass
#
#       async def get_by_username(self, username: str) -> Optional[User]:
#           """Cherche un utilisateur par nom d'utilisateur."""
#           pass
#
#       async def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
#           """Liste les utilisateurs actifs."""
#           pass
#
#       async def update_last_login(self, user_id: int):
#           """Met à jour le champ last_login."""
#           pass

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from datetime import datetime
from typing import Optional, Dict, List
from app.core.config import settings
from app.models.user import User
from app.core.security import hash_password

class UserRepository:
    def __init__(self, es: AsyncElasticsearch):
        self.es = es
        self.index = settings.ELASTICSEARCH_INDEX_USERS
    
    async def create_user(self, user_data: dict) -> dict:
        """Crée un nouvel utilisateur dans Elasticsearch"""
        user_data["password_hash"] = hash_password(user_data.pop("password"))
        user_data["created_at"] = datetime.now().isoformat()
        user_data["is_active"] = True
        user_data["mfa_enabled"] = False
        
        response = await self.es.index(
            index=self.index,
            body=user_data,
            refresh=True
        )
        
        user_data["id"] = response["_id"]
        return user_data
    
    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """Récupère un utilisateur par son nom d'utilisateur"""
        query = {
            "query": {
                "term": {"username": username}
            }
        }
        response = await self.es.search(index=self.index, body=query)
        hits = response["hits"]["hits"]
        
        if not hits:
            return None
        
        doc = hits[0]
        user = doc["_source"]
        user["id"] = doc["_id"]
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Récupère un utilisateur par son email"""
        query = {
            "query": {
                "term": {"email": email}
            }
        }
        response = await self.es.search(index=self.index, body=query)
        hits = response["hits"]["hits"]
        
        if not hits:
            return None
        
        doc = hits[0]
        user = doc["_source"]
        user["id"] = doc["_id"]
        return user
    
    async def update_user(self, user_id: str, update_data: dict) -> bool:
        """Met à jour un utilisateur"""
        try:
            response = await self.es.update(
                index=self.index,
                id=user_id,
                body={"doc": update_data},
                refresh=True
            )
            return response["result"] == "updated"
        except NotFoundError:
            return False
    
    async def update_last_login(self, username: str) -> bool:
        """Met à jour la date de dernière connexion"""
        user = await self.get_user_by_username(username)
        if not user:
            return False
        
        return await self.update_user(
            user["id"], 
            {"last_login": datetime.now().isoformat()}
        )
    
    async def delete_user(self, username: str) -> bool:
        """Désactive un utilisateur"""
        user = await self.get_user_by_username(username)
        if not user:
            return False
        
        return await self.update_user(user["id"], {"is_active": False})
    
    async def list_users(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """Liste les utilisateurs actifs"""
        query = {
            "query": {"term": {"is_active": True}},
            "from": offset,
            "size": limit
        }
        response = await self.es.search(index=self.index, body=query)
        users = []
        for hit in response["hits"]["hits"]:
            user = hit["_source"]
            user["id"] = hit["_id"]
            users.append(user)
        return users


