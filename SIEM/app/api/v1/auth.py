# app/api/v1/auth.py
# -------------------------------
# Endpoints /api/v1/auth — Authentification
#
# Ce que tu dois mettre ici :
#
#   from fastapi import APIRouter, Depends, HTTPException
#   from fastapi.security import OAuth2PasswordRequestForm
#   from app.schemas.user_schemas import TokenResponse, UserCreate, UserResponse
#   from app.services.auth import AuthService
#   from app.api.dependencies import get_current_user
#
#   router = APIRouter()
#
#   @router.post("/login", response_model=TokenResponse)
#   async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#       """Authentification par email/mot de passe -> JWT."""
#       pass
#
#   @router.post("/refresh", response_model=TokenResponse)
#   async def refresh_token(refresh_token: str):
#       """Rafraîchir le token JWT."""
#       pass
#
#   @router.post("/logout")
#   async def logout(token: str = Depends(oauth2_scheme)):
#       """Révoquer le token (invalider côté Redis)."""
#       pass
#
#   @router.post("/mfa/setup")
#   async def setup_mfa(current_user = Depends(get_current_user)):
#       """Configurer l'authentification multi-facteurs (TOTP)."""
#       pass
#
#   @router.post("/mfa/verify")
#   async def verify_mfa(code: str, current_user = Depends(get_current_user)):
#       """Vérifier un code TOTP."""
#       pass
#
#   @router.get("/me", response_model=UserResponse)
#   async def get_me(current_user = Depends(get_current_user)):
#       """Profil de l'utilisateur connecté."""
#       return current_user


# app/api/v1/auth.py
from fastapi import APIRouter, Depends, Request
from app.services.auth import AuthService
from app.repositories.user_repo import UserRepository
from app.repositories.audit_repo import AuditRepository
from app.core.elasticsearch import get_es
from app.schemas.user_schemas import UserLogin
from app.api.dependencies import oauth2_scheme, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
async def login(
    login_data: UserLogin,
    request: Request,
    es=Depends(get_es)
):
    """Authentification utilisateur avec MFA"""
    user_repo = UserRepository(es)
    audit_repo = AuditRepository(es)
    auth_service = AuthService(user_repo, audit_repo)
    
    # Récupérer l'IP du client
    client_ip = request.client.host if request.client else None
    
    result = await auth_service.authenticate_user(
        username=login_data.username,
        password=login_data.password,
        mfa_code=login_data.mfa_code,
        ip_address=client_ip
    )
    
    return result

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: dict = Depends(get_current_user),
    es=Depends(get_es)
):
    """Déconnexion utilisateur"""
    user_repo = UserRepository(es)
    audit_repo = AuditRepository(es)
    auth_service = AuthService(user_repo, audit_repo)
    
    await auth_service.logout(current_user["id"], current_user["username"])
    
    return {"message": "Déconnexion réussie"}