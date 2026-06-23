# app/utils/security.py
# -------------------------------
# Fonctions de sécurité (hash, JWT, TOTP)
#
# Ce que tu dois mettre ici :
#
#   from passlib.context import CryptContext
#   from datetime import datetime, timedelta, timezone
#   from jose import jwt, JWTError
#   from app.core.config import settings
#   import pyotp
#
#   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
#   # --- Hash des mots de passe ---
#   def hash_password(password: str) -> str:
#       """Hash un mot de passe avec bcrypt."""
#       return pwd_context.hash(password)
#
#   def verify_password(plain_password: str, hashed_password: str) -> bool:
#       """Vérifie un mot de passe contre son hash."""
#       return pwd_context.verify(plain_password, hashed_password)
#
#   # --- JWT ---
#   def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
#       """Crée un token JWT d'accès."""
#       to_encode = data.copy()
#       expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.JWT_EXPIRATION_MINUTES))
#       to_encode.update({"exp": expire})
#       return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
#
#   def create_refresh_token(data: dict) -> str:
#       """Crée un refresh token JWT."""
#       to_encode = data.copy()
#       expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)
#       to_encode.update({"exp": expire, "type": "refresh"})
#       return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
#
#   def decode_token(token: str) -> dict | None:
#       """Décode et valide un token JWT."""
#       try:
#           payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
#           return payload
#       except JWTError:
#           return None
#
#   # --- MFA / TOTP ---
#   def generate_totp_secret() -> str:
#       """Génère une clé secrète TOTP."""
#       return pyotp.random_base32()
#
#   def get_totp_uri(secret: str, email: str) -> str:
#       """Génère l'URI à mettre dans le QR code pour l'app d'authentification."""
#       return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name="Smart SIEM")
#
#   def verify_totp(secret: str, code: str) -> bool:
#       """Vérifie un code TOTP."""
#       totp = pyotp.TOTP(secret)
#       return totp.verify(code)
