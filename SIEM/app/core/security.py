import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from app.core.config import settings

# --- Hachage des mots de passe (bcrypt direct) ---
def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe par rapport à son hash"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# --- Gestion des tokens JWT ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un token d'accès JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Crée un token de rafraîchissement JWT"""
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Décode un token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError(f"Token invalide: {str(e)}")

def get_token_data(token: str) -> dict:
    """Extrait les données du token (username, role, perimeter)"""
    payload = decode_token(token)
    return {
        "username": payload.get("sub"),
        "role": payload.get("role"),
        "perimeter": payload.get("perimeter", [])
    }

# --- MFA TOTP ---
import pyotp
import qrcode
from io import BytesIO
import base64

def generate_mfa_secret() -> str:
    """Génère un secret TOTP pour la MFA"""
    return pyotp.random_base32()

def get_mfa_uri(username: str, secret: str, issuer: str = "SmartSIEM") -> str:
    """Génère l'URI pour le QR Code MFA"""
    return pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer)

def generate_qr_code(uri: str) -> str:
    """Génère un QR Code en base64 pour l'affichage"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def verify_mfa(secret: str, code: str) -> bool:
    """Vérifie un code TOTP"""
    if not secret or not code:
        return False
    totp = pyotp.TOTP(secret)
    return totp.verify(code)