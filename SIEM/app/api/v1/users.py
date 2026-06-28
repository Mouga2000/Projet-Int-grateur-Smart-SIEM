# app/api/v1/users.py
# -------------------------------
# Endpoints /api/v1/users — Gestion des utilisateurs


from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.repositories.audit_repo import AuditRepository
from app.repositories.user_repo import UserRepository
from app.schemas.user_schemas import (
    UserCreate,
    UserResponse,
    UserUpdatePerimeter,
    UserUpdateRole,
)
from app.utils.tags import Role

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
async def list_users(
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Liste tous les utilisateurs (réservé aux administrateurs)"""
    user_repo = UserRepository(db)
    users = await user_repo.list_users()
    return users


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Crée un nouvel utilisateur (réservé aux administrateurs)"""
    user_repo = UserRepository(db)

    existing = await user_repo.get_user_by_username(user_data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")

    new_user = await user_repo.create_user(user_data.dict())

    # Journalisation
    audit_repo = AuditRepository(db)
    await audit_repo.log_user_management(
        admin_id=str(current_user["id"]),
        action="create_user",
        target_username=user_data.username,
        details={"role": user_data.role.value, "email": user_data.email},
    )

    return new_user


@router.post("/setup", response_model=UserResponse)
async def setup_first_admin(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Crée le premier administrateur (bootstrap initial).
    Accessible uniquement si aucun utilisateur n'existe encore.
    """
    user_repo = UserRepository(db)

    existing_users = await user_repo.list_users(limit=1)
    if existing_users:
        raise HTTPException(
            status_code=403,
            detail="Un administrateur existe déjà. Connectez-vous ou contactez-le.",
        )

    existing = await user_repo.get_user_by_username(user_data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")

    user_data.role = "administrateur"
    new_user = await user_repo.create_user(user_data.dict())
    return new_user


@router.put("/{username}/role", response_model=UserResponse)
async def update_user_role(
    username: str,
    data: UserUpdateRole,
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Modifie le rôle d'un utilisateur (admin uniquement)."""
    user_repo = UserRepository(db)

    user = await user_repo.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    await user_repo.update_user(user["id"], {"role": data.role.value})

    # Journalisation
    audit_repo = AuditRepository(db)
    await audit_repo.log_user_management(
        admin_id=str(current_user["id"]),
        action="update_role",
        target_username=username,
        details={"old_role": user.get("role"), "new_role": data.role.value},
    )

    updated = await user_repo.get_user_by_username(username)
    return updated


@router.put("/{username}/perimeter", response_model=UserResponse)
async def update_user_perimeter(
    username: str,
    data: UserUpdatePerimeter,
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db),
):
    """Modifie le périmètre fonctionnel d'un utilisateur (admin uniquement)."""
    user_repo = UserRepository(db)

    user = await user_repo.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    await user_repo.update_user(
        user["id"], {"perimeter": [p.value for p in data.perimeter]}
    )

    # Journalisation
    audit_repo = AuditRepository(db)
    await audit_repo.log_user_management(
        admin_id=str(current_user["id"]),
        action="update_perimeter",
        target_username=username,
        details={
            "old_perimeter": user.get("perimeter"),
            "new_perimeter": [p.value for p in data.perimeter],
        },
    )

    updated = await user_repo.get_user_by_username(username)
    return updated


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Récupère les informations de l'utilisateur connecté"""
    return current_user
