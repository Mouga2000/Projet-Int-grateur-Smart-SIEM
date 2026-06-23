# app/schemas/user_schemas.py
# -------------------------------
# Schémas Pydantic pour les utilisateurs et l'authentification
#
# Ce que tu dois mettre ici :
#
#   from pydantic import BaseModel, EmailStr, Field
#   from datetime import datetime
#   from typing import Optional
#   from enum import Enum
#
#   class UserRole(str, Enum):
#       ADMIN = "admin"
#       ANALYST = "analyst"
#       VIEWER = "viewer"
#       AUTOMATION = "automation"
#
#   class UserCreate(BaseModel):
#       email: EmailStr
#       username: str = Field(..., min_length=3, max_length=100)
#       password: str = Field(..., min_length=8)
#       full_name: Optional[str] = None
#       role: UserRole = UserRole.VIEWER
#
#   class UserUpdate(BaseModel):
#       email: Optional[EmailStr] = None
#       full_name: Optional[str] = None
#       role: Optional[UserRole] = None
#       is_active: Optional[bool] = None
#
#   class UserResponse(BaseModel):
#       id: int
#       email: str
#       username: str
#       full_name: Optional[str]
#       role: UserRole
#       is_active: bool
#       is_mfa_enabled: bool
#       last_login: Optional[datetime]
#       created_at: datetime
#
#   class UserListResponse(BaseModel):
#       items: list[UserResponse]
#       total: int
#       page: int
#       size: int
#
#   # --- Auth ---
#   class TokenResponse(BaseModel):
#       access_token: str
#       refresh_token: str
#       token_type: str = "bearer"
#       expires_in: int
#
#   class LoginRequest(BaseModel):
#       email: str
#       password: str

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str  # "lecteur", "analyste", "rssi", "administrateur"
    perimeter: List[str] = []

class UserLogin(BaseModel):
    username: str
    password: str
    mfa_code: Optional[str] = None

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: str
    role: str
    perimeter: List[str]

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str
    perimeter: List[str]
    mfa_enabled: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class UserUpdateRole(BaseModel):
    role: str