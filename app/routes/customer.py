# роутер операция с покупателями
from datetime import datetime
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from dependencies.dependency import get_db
from models.customer_model import Customer
from schemas.customer import CustomerCreateSchema, CustomerDeleteSchema, CustomerUpdateSchema

customer_router = APIRouter(
    prefix='/customer',
    tags=['Customers']
)
templates = Jinja2Templates(directory="templates")

# вывести пользрвателей
@customer_router.get("/users/", response_class = HTMLResponse)
async def get_users_page(request:Request, db: Session = Depends(get_db)):
    stmnt = select(Customer)
    users:list = db.scalars(stmnt).all()
    context:dict = {}
    i:int = 1
    for user in users:
        new_el = {str(i): user.name}
        context.update(new_el)
        i += 1
    return templates.TemplateResponse("users.html", {"request": request, "context": context})

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

# изменить пользователя
@customer_router.post("/userchange/")
async def change_task(request:Request, customer_upd: CustomerUpdateSchema, db: Session = Depends(get_db)):
    name = customer_upd.name
    stmnt = select(Customer).where(Customer.id == customer_upd.id)
    customer = db.scalars(stmnt).one()
    match customer_upd.field:
        case 'email': customer.email = customer_upd.new_value
        case 'password': customer.password = customer_upd.new_value
        case 'name': customer.name = customer_upd.new_value
        case 'role': customer.role = customer_upd.new_value
    customer.data_change = datetime.utcnow()
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return RedirectResponse(url="/customer/users", status_code=status.HTTP_302_FOUND)

# удалить пользователя
@customer_router.post("/userdel/")
async def del_task(request:Request, customer_del: CustomerDeleteSchema, db: Session = Depends(get_db)):
    stmnt = select(Customer).where(Customer.id == customer_del.id)
    customer = db.scalars(stmnt).one()
    db.delete(customer)
    db.commit()
    return RedirectResponse(url="/customer/users", status_code=status.HTTP_302_FOUND)