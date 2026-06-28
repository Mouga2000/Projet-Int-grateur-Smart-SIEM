# app/api/v1/users.py
# -------------------------------
# Endpoints /api/v1/users — Gestion des utilisateurs


from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import get_current_user, require_role
from app.utils.tags import Role
from app.schemas.user_schemas import UserCreate, UserResponse, UserUpdateRole, UserUpdatePerimeter
from app.repositories.user_repo import UserRepository
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
async def list_users(
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db)
):
    """Liste tous les utilisateurs (réservé aux administrateurs)"""
    user_repo = UserRepository(db)
    users = await user_repo.list_users()
    return users

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db)
):
    """Crée un nouvel utilisateur (réservé aux administrateurs)"""
    user_repo = UserRepository(db)

    existing = await user_repo.get_user_by_username(user_data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")

    new_user = await user_repo.create_user(user_data.dict())
    return new_user

@router.post("/setup", response_model=UserResponse)
async def setup_first_admin(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crée le premier administrateur (bootstrap initial).
    Accessible uniquement si aucun utilisateur n'existe encore.
    """
    user_repo = UserRepository(db)

    existing_users = await user_repo.list_users(limit=1)
    if existing_users:
        raise HTTPException(
            status_code=403,
            detail="Un administrateur existe déjà. Connectez-vous ou contactez-le."
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
    db: AsyncSession = Depends(get_db)
):
    """Modifie le rôle d'un utilisateur (admin uniquement)."""
    user_repo = UserRepository(db)

    user = await user_repo.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    await user_repo.update_user(user["id"], {"role": data.role.value})

    updated = await user_repo.get_user_by_username(username)
    return updated


@router.put("/{username}/perimeter", response_model=UserResponse)
async def update_user_perimeter(
    username: str,
    data: UserUpdatePerimeter,
    current_user: dict = Depends(require_role([Role.ADMINISTRATEUR])),
    db: AsyncSession = Depends(get_db)
):
    """Modifie le périmètre fonctionnel d'un utilisateur (admin uniquement)."""
    user_repo = UserRepository(db)

    user = await user_repo.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    await user_repo.update_user(user["id"], {
        "perimeter": [p.value for p in data.perimeter]
    })

    updated = await user_repo.get_user_by_username(username)
    return updated


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user)
):
    """Récupère les informations de l'utilisateur connecté"""
    return current_user