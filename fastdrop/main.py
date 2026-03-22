from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastdrop.dependencies import create_db_and_tables

from fastdrop.routers import api, pages
from fastdrop.config import SECRET_KEY

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting the app")
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.include_router(api.router, prefix="/api")
app.include_router(pages.router)

@app.get("/")
async def hello_world():
    return {"response": "Hello world"}
