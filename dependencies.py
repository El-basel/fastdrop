from .config import DATABASE_URL

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Cookie, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import SQLModel, create_engine, Session
import jwt

from .utils import decode_token
from .models import User
engine = create_engine(DATABASE_URL, echo=False)
def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    # SQLModel.metadata.drop_all(engine)
    print("Creating Database and tables")
    SQLModel.metadata.create_all(engine)

SessionDep = Annotated[Session, Depends(get_session)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login', auto_error=False)

AuthBearerDep = Annotated[str | None, Depends(oauth2_scheme)]
# Making AutCookieDep in Annotated[] would make Swagger UI mark it as required
# so changed it be used as a default value
AuthCookieDep = Cookie(default=None, alias="access_token")

async def get_current_user(bearer_token: AuthBearerDep, session: SessionDep, cookie_token = AuthCookieDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    access_token = bearer_token or cookie_token
    if not access_token:
        return None
    
    try:
        payload = decode_token(access_token)
        user_id = UUID(payload.get('sub'))
        user = session.get(User, user_id)

        if user and user.is_active:
            return user
    except:
        raise credentials_exception
    return None


GetUserDep = Annotated[User | None, Depends(get_current_user)]