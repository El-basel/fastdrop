from contextlib import asynccontextmanager

from fastapi import FastAPI

from .dependencies import create_db_and_tables

from .routers import files, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting the app")
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(files.router)
app.include_router(auth.router)

@app.get("/")
async def hello_world():
    return {"response": "Hello world"}
