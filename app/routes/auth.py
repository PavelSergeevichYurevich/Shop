from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

app_router = APIRouter(
    prefix='/app',
    tags=['Main/Login/Register']
)
templates = Jinja2Templates(directory="templates")

@app_router.get("/")
async def login(request:Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app_router.get("/login/")
async def login(request:Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app_router.get("/register/")
async def login(request:Request):
    return templates.TemplateResponse(request=request, name="register.html")



