# роутер операция с покупателями
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session
from routes.auth import hashing_pass
from dependencies.dependency import get_db
from models.models import Customer
from schemas.schemas import CustomerCreateSchema, CustomerUpdateSchema

customer_router = APIRouter(
    prefix='/customer',
    tags=['Customers']
)
templates = Jinja2Templates(directory="templates")

# вывести пользoвателей
@customer_router.get("/show/", response_model=List[CustomerCreateSchema])
async def get_customers(request:Request, db: Session = Depends(get_db)):
    stmnt = select(Customer)
    users:list = db.scalars(stmnt).all()
    return users

# создать пользователя
@customer_router.post("/add/", response_model=CustomerCreateSchema)
async def add_customer(request:Request, customer: CustomerCreateSchema, password: str, db: Session = Depends(get_db)):
    hashed_password = hashing_pass(password)
    new_customer = Customer(
        email = customer.email,
        hashed_password = hashed_password,
        name = customer.name
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer
    # return RedirectResponse(url="/app/login/", status_code=status.HTTP_302_FOUND)

# изменить пользователя
@customer_router.put(path='/update/')
async def change_customer(request:Request, customer_id:int, customer_upd: CustomerUpdateSchema, db: Session = Depends(get_db)):
    stmnt = update(Customer).where(Customer.id == customer_id).values(
        email = customer_upd.email,
        password = customer_upd.password,
        name = customer_upd.name,
        role = customer_upd.role,
        data_change = datetime.utcnow()
    )
    customer = db.execute(stmnt)
    db.commit()
    return customer

# удалить пользователя
@customer_router.delete(path='/delete/')
async def del_customer(request:Request, id:int, db: Session = Depends(get_db)):
    stmnt = delete(Customer).where(Customer.id == id)
    customer = db.execute(stmnt)
    db.commit()
    return customer