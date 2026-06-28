# app/api/dependencies.py
# -------------------------------
# Dépendances FastAPI réutilisables (injection de dépendances)
#
# Ce que tu dois mettre ici :
#
#   from fastapi import Depends, HTTPException, status
#   from fastapi.security import OAuth2PasswordBearer
#   from app.core.elasticsearch import get_es
#   from app.core.security import decode_token
#   from app.repositories.user_repo import UserRepository
#
#   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
#
#   ROLES : "lecteur", "analyste", "rssi", "administrateur"
#
#   async def get_current_user(token, es) -> dict:
#       """Valide le token JWT et retourne l'utilisateur courant."""
#       pass
#
#   def require_role(allowed_roles: list):
#       """Vérifie que l'utilisateur a le bon rôle."""
#       pass
#
#   def require_permissions(required_permissions: list):
#       """Vérifie que l'utilisateur a les permissions requises."""
#       pass


from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_token
from app.repositories.user_repo import UserRepository
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.tags import Role
from typing import List

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Récupère l'utilisateur actuel à partir du token JWT (PostgreSQL).
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

        # 2. Récupérer l'utilisateur dans PostgreSQL
        user_repo = UserRepository(db)
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
    role = Role(current_user.get("role", "lecteur"))
    return role.get_permissions()

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

def require_role(allowed_roles: List[Role]):
    """
    Vérifie que l'utilisateur a l'un des rôles autorisés.

    Utilisation : require_role([Role.ADMINISTRATEUR])
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
