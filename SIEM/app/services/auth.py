# app/services/auth.py
# -------------------------------
# Service d'authentification (JWT, MFA, sessions)

from fastapi import HTTPException, status
from app.core.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token, 
    verify_mfa
)
from app.repositories.user_repo import UserRepository
from app.repositories.audit_repo import AuditRepository
from app.core.config import settings
from app.core.elasticsearch import get_es

class AuthService:
    def __init__(self, user_repo: UserRepository, audit_repo: AuditRepository):
        self.user_repo = user_repo
        self.audit_repo = audit_repo
    
    async def authenticate_user(
        self, 
        username: str, 
        password: str, 
        mfa_code: str = None, 
        ip_address: str = None
    ):
        """Authentifie un utilisateur et génère les tokens"""
        # 1. Récupérer l'utilisateur
        user = await self.user_repo.get_user_by_username(username)
        
        if not user:
            await self._log_auth_attempt("system", username, "login", "failed", ip_address)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nom d'utilisateur ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 2. Vérifier le mot de passe
        if not verify_password(password, user["password_hash"]):
            await self._log_auth_attempt(user["id"], username, "login", "failed", ip_address)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nom d'utilisateur ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 3. Vérifier si l'utilisateur est actif
        if not user.get("is_active", True):
            await self._log_auth_attempt(user["id"], username, "login", "failed", ip_address)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte désactivé"
            )
        
        # 4. Vérifier la MFA
        if user.get("mfa_enabled", False):
            if not mfa_code:
                await self._log_auth_attempt(user["id"], username, "login", "failed", ip_address)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Code MFA requis"
                )
            if not verify_mfa(user.get("mfa_secret"), mfa_code):
                await self._log_auth_attempt(user["id"], username, "login", "failed", ip_address)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Code MFA invalide"
                )
        
        # 5. Mise à jour de la dernière connexion
        await self.user_repo.update_last_login(username)
        
        # 6. Journalisation de la réussite 
        await self._log_auth_attempt(user["id"], username, "login", "success", ip_address)
        
        # 7. Générer les tokens
        token_data = {
            "sub": username,
            "role": user["role"],
            "perimeter": user.get("perimeter", [])
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "perimeter": user.get("perimeter", []),
                "mfa_enabled": user.get("mfa_enabled", False)
            }
        }
    
    async def _log_auth_attempt(
        self, 
        user_id: str, 
        username: str, 
        action: str, 
        result: str, 
        ip_address: str = None
    ):
        """Journalise une tentative d'authentification"""
        if action == "login":
            await self.audit_repo.log_login_attempt(
                user_id, username, result == "success", ip_address
            )
        elif action == "mfa":
            await self.audit_repo.log_mfa_verification(
                user_id, username, result == "success"
            )
    
    async def refresh_token(self, refresh_token: str):
        # ... (code existant)
        pass
    
    async def logout(self, user_id: str, username: str):
        """Journalise la déconnexion"""
        await self.audit_repo.log_logout(user_id, username)
        return {"message": "Déconnexion réussie"}