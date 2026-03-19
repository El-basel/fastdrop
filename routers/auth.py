import uuid
from typing import Annotated
from zoneinfo import ZoneInfo
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from sqlmodel import select, Session
from pydantic import EmailStr

from ..dependencies import SessionDep
from ..models import User, Token, UserPublic, UserCreate
from ..utils import hash_password, verify_password, create_access_token
from ..config import IN_PRODUCTION

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

async def register_user(user_data: UserCreate, session: Session):
    user: User | None =session.exec(select(User).where(User.email == user_data.email)).first()
    print("user email is unique")
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

# either set the access token in HttpOnly cookie
# (this will make it easier in the frontend to send the token 
# instead of developer handling it, the browser will take care)
# or Autherization header (this will make it easier for Swagger UI 
# and API testing tools to just set the header)
async def authenticate_and_set_cookie(response: Response, username: str, password: str, session: Session) -> str:
    user: User | None = autheticate_user(username, password, session)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": jsonable_encoder(user.id)})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=IN_PRODUCTION,
        samesite="lax",
        max_age=14*24*60*60
    )
    return access_token

@router.post('/register', response_model=UserPublic)
async def api_register(user_data: UserCreate, session: SessionDep):
    user = await register_user(user_data, session)
    return user

@router.post('/login')
async def api_login(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    access_token = await authenticate_and_set_cookie(response, form_data.username, form_data.password, session)
    return Token(access_token=access_token, token_type="bearer")
