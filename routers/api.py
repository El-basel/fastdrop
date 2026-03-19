from fastapi import APIRouter

from . import files, auth, users

router = APIRouter()

router.include_router(files.router)
router.include_router(auth.router)
router.include_router(users.router)
