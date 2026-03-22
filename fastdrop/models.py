import uuid
from fastdrop.utils import *
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr, computed_field, BaseModel



class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)

class UserCreate(SQLModel):
    email: EmailStr = Field(unique=True, max_length=255)
    full_name: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)

class UserLogin(SQLModel):
    email: EmailStr
    password: str

class User(UserBase, table=True):
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    files: list[File] = Relationship(back_populates="user")
    
class UserPublic(UserBase):
    id: uuid.UUID

class FileBase(SQLModel):
    name: str = Field(max_length=128)
    size: int = Field(default=0, ge=0)
    mime_type: str | None
    

class File(FileBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    extension: str = ""
    expires_at: datetime
    uploaded_at: datetime = Field(default_factory=get_datetime_utc)
    download_count: int  = 0
    is_active: bool = True
    is_deleted: bool = False

    uploaded_by: uuid.UUID | None = Field(nullable=True, default=None, foreign_key="user.id")
    user: User | None = Relationship(back_populates="files")

    @computed_field
    @property
    def stored_path(self) -> str:
        return f"./{self.uploaded_at.year}_{self.uploaded_at.month:02d}/{self.id}{self.extension}"

class FilePublic(FileBase):
    id: uuid.UUID
    download_count: int
    expires_at: datetime
    deletion_token: str | None = None
    @computed_field
    @property
    def download_url(self) -> str:
        return f"/files/{self.id}"

class Token(BaseModel):
    access_token: str
    token_type: str

class DeletionToken(BaseModel):
    file_id: uuid.UUID
    action: str
    exp: datetime