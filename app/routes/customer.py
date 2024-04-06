# роутер операция с покупателями
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from dependencies.dependency import get_db
from models.customer_model import Customer
from schemas.customer import CustomerCreateSchema

customer_router = APIRouter(
    prefix='/customer',
    tags=['Customers']
)
templates = Jinja2Templates(directory="templates")

# создать пользователя
@customer_router.post("/rec/")
async def add_customer(request:Request, customer: CustomerCreateSchema, db: Session = Depends(get_db)):
    new_customer = Customer(
        email = customer.email,
        password = customer.password,
        name = customer.name
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return RedirectResponse(url="/app/login/", status_code=status.HTTP_302_FOUND)