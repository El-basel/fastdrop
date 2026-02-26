import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from pydantic import EmailStr

def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

class UserLogin(SQLModel):
    email: EmailStr
    password: str

class User(UserBase, table=True):
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(default_factory=get_datetime_utc)

class UserPublic(UserBase):
    id: uuid.UUID