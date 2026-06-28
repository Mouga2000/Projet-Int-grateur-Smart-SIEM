# app/models/user.py
# -------------------------------
# Modèle User — stocké dans l'index Elasticsearch "users"
#
# Ce que tu dois mettre ici :
#   from pydantic import BaseModel, Field, EmailStr
#   from typing import Optional, List
#   from datetime import datetime
#
#   class User(BaseModel):
#       id: Optional[str] = None
#       username: str = Field(..., min_length=3, max_length=50)
#       email: EmailStr
#       password_hash: str
#       mfa_secret: Optional[str] = None
#       mfa_enabled: bool = False
#       role: str  # "lecteur", "analyste", "rssi", "administrateur"
#       perimeter: List[str] = []
#       created_at: datetime = Field(default_factory=datetime.now)
#       last_login: Optional[datetime] = None
#       is_active: bool = True
#
#       def to_es_document(self) -> dict:
#           return self.model_dump(exclude={"id"})


from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from app.utils.tags import Role, Perimeter

class User(BaseModel):
    id: Optional[str] = None
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password_hash: str
    mfa_secret: Optional[str] = None
    mfa_enabled: bool = False
    role: Role
    perimeter: List[Perimeter] = []
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_active: bool = True

    def to_es_document(self) -> dict:
        """Convertit le modèle en document Elasticsearch"""
        return self.model_dump(exclude={"id"})
