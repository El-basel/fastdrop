from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from fastdrop.dependencies import SessionDep
from fastdrop.models import Token, UserPublic, UserCreate
from fastdrop.services.auth import authenticate_and_set_cookie, register_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
    )


@router.post('/register', response_model=UserPublic)
async def api_register(user_data: UserCreate, session: SessionDep):
    user = await register_user(user_data, session)
    return user

@router.post('/login')
async def api_login(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    access_token = await authenticate_and_set_cookie(response, form_data.username, form_data.password, session)
    return Token(access_token=access_token, token_type="bearer")
