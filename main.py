import shutil
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from sqlmodel import Field, SQLModel, create_engine
from fastapi import FastAPI, UploadFile
from .models import *
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "")
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifspan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifspan=lifspan)


@app.get("/")
async def hello_world():
    return {"response": "Hello world"}


@app.post("/file")
async def uplode_file(in_file: UploadFile):
    path = f"./files/{in_file.filename}"
    with open(path, "wb+") as out_file:
        shutil.copyfileobj(in_file.file, out_file)
    return {"file name": in_file.filename, "type": in_file.content_type}