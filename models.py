import uuid
from datetime import datetime, timezone, timedelta
from sqlmodel import SQLModel, Field
from pydantic import EmailStr, computed_field


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

class FileBase(SQLModel):
    name: str = Field(max_length=128)
    size: int = Field(ge=0)
    mime_type: str
    

class File(FileBase, table=True):
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    extension: str = Field(default="") 
    uploaded_by: uuid.UUID | None = Field(foreign_key="user.id")
    expires_at: datetime
    uploaded_at: datetime | None = Field(default_factory=get_datetime_utc)
    download_count: int | None = Field(default=0)
    delete_token: str | None = None
    is_active: bool = True

class FilePublic(FileBase):
    id: uuid.UUID
    download_count: int
    expires_at: datetime

    @computed_field
    @property
    def download_url(self) -> str:
        return f"/files/{self.id}"