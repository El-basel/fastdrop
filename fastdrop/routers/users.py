from fastapi import APIRouter
from fastdrop.dependencies import GetUserDep
from fastdrop.services.users import dashboard

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.get("/me")
async def api_dashboard(user: GetUserDep):
    return await dashboard(user)