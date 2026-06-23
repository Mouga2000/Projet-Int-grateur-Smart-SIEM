# app/api/v1/users.py
# -------------------------------
# Endpoints /api/v1/users — Gestion des utilisateurs
#
# Ce que tu dois mettre ici :
#
#   from fastapi import APIRouter, Depends, Query
#   from app.schemas.user_schemas import UserCreate, UserUpdate, UserResponse, UserListResponse
#   from app.repositories.user_repo import UserRepository
#   from app.api.dependencies import get_current_user, get_current_admin
#   from app.core.database import get_db
#
#   router = APIRouter()
#
#   @router.get("/", response_model=UserListResponse)
#   async def list_users(
#       page: int = Query(1, ge=1),
#       size: int = Query(50, le=200),
#       admin = Depends(get_current_admin),
#       db = Depends(get_db),
#   ):
#       """Liste des utilisateurs (admin only)."""
#       pass
#
#   @router.post("/", response_model=UserResponse, status_code=201)
#   async def create_user(
#       data: UserCreate,
#       admin = Depends(get_current_admin),
#       db = Depends(get_db),
#   ):
#       """Créer un utilisateur (admin only)."""
#       pass
#
#   @router.get("/{user_id}", response_model=UserResponse)
#   async def get_user(
#       user_id: int,
#       current_user = Depends(get_current_user),
#       db = Depends(get_db),
#   ):
#       """Détail d'un utilisateur."""
#       pass
#
#   @router.put("/{user_id}", response_model=UserResponse)
#   async def update_user(
#       user_id: int,
#       data: UserUpdate,
#       current_user = Depends(get_current_user),
#       db = Depends(get_db),
#   ):
#       """Modifier un utilisateur."""
#       pass
#
#   @router.delete("/{user_id}", status_code=204)
#   async def delete_user(
#       user_id: int,
#       admin = Depends(get_current_admin),
#       db = Depends(get_db),
#   ):
#       """Supprimer un utilisateur (admin only)."""
#       pass


from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import get_current_user, require_role, require_permissions
from app.schemas.user_schemas import UserCreate, UserResponse
from app.repositories.user_repo import UserRepository
from app.core.elasticsearch import get_es
from app.core.security import hash_password
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
async def list_users(
    current_user: dict = Depends(require_role(["administrateur"])),
    es=Depends(get_es)
):
    """Liste tous les utilisateurs (réservé aux administrateurs)"""
    user_repo = UserRepository(es)
    users = await user_repo.list_users()
    return users

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(require_role(["administrateur"])),
    es=Depends(get_es)
):
    """Crée un nouvel utilisateur (réservé aux administrateurs)"""
    user_repo = UserRepository(es)
    
    # Vérifier si l'utilisateur existe déjà
    existing = await user_repo.get_user_by_username(user_data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
    
    # Créer l'utilisateur
    new_user = await user_repo.create_user(user_data.dict())
    return new_user

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user)
):
    """Récupère les informations de l'utilisateur connecté"""
    return current_user