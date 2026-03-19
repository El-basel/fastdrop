from typing import Annotated

from fastapi import APIRouter, Request, Form, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..config import TEMPLATES_DIR
from ..dependencies import SessionDep
from .auth import authenticate_and_set_cookie


router = APIRouter()

templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.get("/login", response_class=HTMLResponse)
async def web_login_view(request: Request):
    context = {
        "error": request.session.pop("error", False),
        "msg": request.session.pop("msg", None)
    }
    return templates.TemplateResponse(
        request=request, name="login.html", context=context
    )

@router.post("/login")
async def web_login_form(request: Request, response: Response, username: Annotated[str, Form()], password: Annotated[str, Form()], session: SessionDep):
    if not username or not password:
        request.session["error"] = True
        request.session["msg"] = "Please fill in both username and password"
        redirect_failuer = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    else:
        try:
            await authenticate_and_set_cookie(response, username, password, session)
            return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
        except HTTPException as e:
            request.session["error"] = True
            request.session["msg"] = e.detail
            redirect_failuer = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return redirect_failuer
        