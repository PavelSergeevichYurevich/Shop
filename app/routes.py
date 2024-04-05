from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

shop_router = APIRouter()
templates = Jinja2Templates(directory="templates")

@shop_router.get("/login/")
async def login(request:Request):
    return templates.TemplateResponse(request=request, name="login.html")

@shop_router.get("/register/")
async def login(request:Request):
    return templates.TemplateResponse(request=request, name="register.html")

