from .config import DATABASE_URL

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import SQLModel, create_engine, Session
engine = create_engine(DATABASE_URL, echo=False)
def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    # SQLModel.metadata.drop_all(engine)
    print("Creating Database and tables")
    SQLModel.metadata.create_all(engine)

SessionDep = Annotated[Session, Depends(get_session)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')