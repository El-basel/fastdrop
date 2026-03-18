import uuid
from typing import Annotated
from zoneinfo import ZoneInfo
from datetime import timedelta

from fastapi import APIRouter, Body, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from sqlmodel import select
from pydantic import EmailStr

from ..dependencies import SessionDep
from ..models import User, Token, UserPublic, UserCreate
from ..utils import hash_password, verify_password, create_access_token

DUMMY_HASH = hash_password("DUMMY_HASH")
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
    )

def autheticate_user(email: EmailStr, password: str, session) -> User | None:
    user: User | None = session.exec(select(User).where(User.email == email)).first()
    if not user:
        verify_password(password, DUMMY_HASH)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


@router.post('/register', response_model=UserPublic)
async def user_register(user_data: UserCreate, session: SessionDep):
    user: User | None = session.exec(select(User).where(User.email == user_data.email)).first()
    if user:
        raise HTTPException(status_code=409, detail="User with this email already exists")
    password = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=password,
        full_name=user_data.full_name
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post('/login')
async def user_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    user: User | None = autheticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": jsonable_encoder(user.id)})
    return Token(access_token=access_token, token_type="bearer")
