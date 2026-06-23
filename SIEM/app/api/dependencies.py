# app/api/dependencies.py
# -------------------------------
# Dépendances FastAPI réutilisables (injection de dépendances)
#
# Ce que tu dois mettre ici :
#
#   from fastapi import Depends, HTTPException, status
#   from fastapi.security import OAuth2PasswordBearer
#   from sqlalchemy.ext.asyncio import AsyncSession
#   from app.core.database import get_db
#   from app.core.elasticsearch import get_es_client
#   from app.core.redis import get_cache
#   from app.repositories.user_repo import UserRepository
#   from app.services.auth import decode_access_token
#
#   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
#
#   async def get_current_user(
#       token: str = Depends(oauth2_scheme),
#       db: AsyncSession = Depends(get_db),
#   ):
#       """Valide le token JWT et retourne l'utilisateur courant."""
#       payload = decode_access_token(token)
#       if payload is None:
#           raise HTTPException(status_code=401, detail="Invalid token")
#       user_repo = UserRepository(db)
#       user = await user_repo.get_by_id(payload.get("sub"))
#       if user is None:
#           raise HTTPException(status_code=401, detail="User not found")
#       return user
#
#   async def get_current_admin(current_user = Depends(get_current_user)):
#       """Vérifie que l'utilisateur est admin."""
#       if current_user.role != "admin":
#           raise HTTPException(status_code=403, detail="Admin access required")
#       return current_user
#
#   # Autres dépendances possibles :
#   # - Pagination (page, size) -> Query params
#   # - Filtres temporels (date_from, date_to)
#   # - Rate limiter (avec Redis)
#   # - Audit trail (logger les actions)


from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_token, get_token_data
from app.repositories.user_repo import UserRepository
from app.core.elasticsearch import get_es
from typing import List, Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# --- Définition des rôles et permissions ---
ROLE_PERMISSIONS = {
    "lecteur": ["read:logs", "read:dashboard", "read:reports"],
    "analyste": ["read:logs", "read:dashboard", "read:reports", "write:alerts", "read:incidents", "write:incidents"],
    "rssi": ["read:dashboard", "read:reports", "write:reports"],
    "administrateur": ["*"]  # Toutes les permissions
}

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    es=Depends(get_es)
) -> dict:
    """
    Récupère l'utilisateur actuel à partir du token JWT
    """
    try:
        # 1. Décoder le token
        payload = decode_token(token)
        username = payload.get("sub")
        
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )
        
        # 2. Récupérer l'utilisateur
        user_repo = UserRepository(es)
        user = await user_repo.get_user_by_username(username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non trouvé"
            )
        
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte désactivé"
            )
        
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )

async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Vérifie que l'utilisateur est actif
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )
    return current_user

async def get_current_user_permissions(
    current_user: dict = Depends(get_current_active_user)
) -> List[str]:
    """
    Récupère les permissions de l'utilisateur en fonction de son rôle
    """
    role = current_user.get("role", "lecteur")
    return ROLE_PERMISSIONS.get(role, [])

def require_permissions(required_permissions: List[str]):
    """
    Décorateur/factory pour vérifier les permissions
    """
    async def permission_checker(
        user_permissions: List[str] = Depends(get_current_user_permissions)
    ):
        # Vérifier si l'utilisateur a les permissions requises
        if "*" in user_permissions:  # Administrateur
            return True
        
        for perm in required_permissions:
            if perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission insuffisante. Requis: {', '.join(required_permissions)}"
                )
        return True
    
    return permission_checker

def require_role(allowed_roles: List[str]):
    """
    Vérifie que l'utilisateur a l'un des rôles autorisés
    """
    async def role_checker(
        current_user: dict = Depends(get_current_active_user)
    ):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rôle insuffisant. Rôle requis: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker