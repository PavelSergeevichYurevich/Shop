from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

auth_router = APIRouter(
    prefix='/auth',
    tags=['Login/Register']
)
templates = Jinja2Templates(directory="templates")

@auth_router.get("/login/")
async def login(request:Request):
    return templates.TemplateResponse(request=request, name="login.html")

@auth_router.get("/register/")
async def login(request:Request):
    return templates.TemplateResponse(request=request, name="register.html")



