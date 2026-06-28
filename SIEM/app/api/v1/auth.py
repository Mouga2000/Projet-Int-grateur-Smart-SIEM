# app/api/v1/auth.py
# -------------------------------
# Endpoints /api/v1/auth — Authentification (PostgreSQL)


from fastapi import APIRouter, Depends, Request, HTTPException
from app.services.auth import AuthService
from app.repositories.user_repo import UserRepository
from app.repositories.audit_repo import AuditRepository
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    generate_mfa_secret, get_mfa_uri, generate_qr_code,
    verify_mfa, verify_password
)
from app.schemas.user_schemas import UserLogin
from app.api.dependencies import oauth2_scheme, get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Schémas MFA ---
class MfaSetupResponse(BaseModel):
    secret: str
    uri: str
    qr_code: str  # base64

class MfaVerifyRequest(BaseModel):
    code: str

class MfaDisableRequest(BaseModel):
    current_password: str

class MfaStatusResponse(BaseModel):
    mfa_enabled: bool

# --- Login ---

@router.post("/login")
async def login(
    login_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Authentification utilisateur avec MFA (stockage PostgreSQL)."""
    user_repo = UserRepository(db)
    audit_repo = AuditRepository(db)
    auth_service = AuthService(user_repo, audit_repo)

    client_ip = request.client.host if request.client else None

    result = await auth_service.authenticate_user(
        username=login_data.username,
        password=login_data.password,
        mfa_code=login_data.mfa_code,
        ip_address=client_ip
    )

    return result

# --- Logout ---

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Déconnexion utilisateur."""
    user_repo = UserRepository(db)
    audit_repo = AuditRepository(db)
    auth_service = AuthService(user_repo, audit_repo)

    await auth_service.logout(current_user["id"], current_user["username"])

    return {"message": "Déconnexion réussie"}

# --- MFA : Voir le statut ---

@router.get("/mfa/status", response_model=MfaStatusResponse)
async def mfa_status(
    current_user: dict = Depends(get_current_user)
):
    """Vérifie si la MFA est activée sur ton compte."""
    return {"mfa_enabled": current_user.get("mfa_enabled", False)}

# --- MFA : Activer (étape 1 : générer le secret) ---

@router.post("/mfa/setup", response_model=MfaSetupResponse)
async def mfa_setup(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Génère un secret TOTP et un QR code pour configurer l'app d'authentification.
    Le secret est sauvegardé mais la MFA n'est pas encore activée.
    """
    user_repo = UserRepository(db)

    secret = generate_mfa_secret()
    uri = get_mfa_uri(current_user["username"], secret)
    qr_code = generate_qr_code(uri)

    await user_repo.update_user(current_user["id"], {"mfa_secret": secret})

    return MfaSetupResponse(secret=secret, uri=uri, qr_code=qr_code)

# --- MFA : Activer (étape 2 : vérifier le code) ---

@router.post("/mfa/verify", response_model=MfaStatusResponse)
async def mfa_verify(
    data: MfaVerifyRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Vérifie un code TOTP avec le secret sauvegardé.
    Si le code est valide, la MFA est activée définitivement.
    """
    secret = current_user.get("mfa_secret")
    if not secret:
        raise HTTPException(status_code=400, detail="Aucun secret MFA trouvé. Fais d'abord /mfa/setup")

    if not verify_mfa(secret, data.code):
        raise HTTPException(status_code=400, detail="Code MFA invalide")

    user_repo = UserRepository(db)
    await user_repo.update_user(current_user["id"], {"mfa_enabled": True})

    return {"mfa_enabled": True}

# --- MFA : Désactiver ---

@router.post("/mfa/disable", response_model=MfaStatusResponse)
async def mfa_disable(
    data: MfaDisableRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Désactive la MFA. Nécessite la confirmation du mot de passe actuel.
    """
    if not verify_password(data.current_password, current_user["password_hash"]):
        raise HTTPException(status_code=400, detail="Mot de passe incorrect")

    user_repo = UserRepository(db)
    await user_repo.update_user(current_user["id"], {
        "mfa_enabled": False,
        "mfa_secret": None
    })

    return {"mfa_enabled": False}
