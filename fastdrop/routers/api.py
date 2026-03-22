from fastapi import APIRouter

from fastdrop.routers import files, auth, users

router = APIRouter()

router.include_router(files.router)
router.include_router(auth.router)
router.include_router(users.router)
