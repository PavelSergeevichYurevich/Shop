from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from dependencies.dependency import get_db
from schemas.customer import CustomerCreateSchema
from models.customer_model import Customer
from sqlalchemy.orm import Session

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

@auth_router.post("/rec/")
async def add_customer(request:Request, customer: CustomerCreateSchema, db: Session = Depends(get_db)):
    new_customer = Customer(
        email = customer.email,
        password = customer.password,
        name = customer.name
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return RedirectResponse(url="/auth/login/", status_code=status.HTTP_302_FOUND)

