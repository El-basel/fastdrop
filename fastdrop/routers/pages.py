from typing import Annotated

from fastapi import APIRouter, Request, Form, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from fastdrop.config import TEMPLATES_DIR
from fastdrop.dependencies import SessionDep, GetUserDep
from fastdrop.models import UserCreate, UserLogin
from fastdrop.services.auth import authenticate_and_set_cookie, register_user
from fastdrop.services.users import dashboard


router = APIRouter()

templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.get("/login", response_class=HTMLResponse)
async def web_login_get(request: Request):
    context = {
        "error": request.session.pop("error", False),
        "msg": request.session.pop("msg", None)
    }
    return templates.TemplateResponse(
        request=request, name="login.html", context=context
    )

@router.post("/login")
async def web_login_post(request: Request, user: Annotated[UserLogin, Form()], session: SessionDep):
    if not user.email or not user.password:
        request.session["error"] = True
        request.session["msg"] = "Please fill in both username and password"
        redirect_failure = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    else:
        try:
            redirect_success = RedirectResponse("/dashboard", status_code=status.HTTP_302_FOUND)
            await authenticate_and_set_cookie(redirect_success, user.email, user.password, session)
            return redirect_success
        except HTTPException as e:
            request.session["error"] = True
            request.session["msg"] = e.detail
            redirect_failure = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return redirect_failure
        

@router.get("/register")
async def web_register_get(request: Request):
    context = {
        "error": request.session.pop("error", False),
        "msg": request.session.pop("msg", None)
    }
    return templates.TemplateResponse(
        request=request, name="signup.html", context=context
    )

@router.post("/register")
async def web_register_post(request: Request, user: Annotated[UserCreate, Form()], session: SessionDep):
    try:
        redirect_success = RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
        created_user = await register_user(user, session)
        return redirect_success
    except HTTPException as e:
        request.session["error"] = True
        request.session["msg"] = e.detail
        redirect_failure = RedirectResponse(url="/register", status_code=status.HTTP_303_SEE_OTHER)
    return redirect_failure

@router.get("/dashboard")
async def web_dashboard_get(request: Request, user: GetUserDep):
    try:
        user_data = await dashboard(user)
        print(user)
        return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user_data": user_data}
        )
    except HTTPException as e:
        request.session["error"] = True
        request.session["msg"] = e.detail
        redirect_failure = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        return redirect_failure
    