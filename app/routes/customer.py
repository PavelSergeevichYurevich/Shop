# роутер операция с покупателями
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
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

# вывести пользрвателей
@customer_router.get("/users/", response_class = HTMLResponse)
async def get_users_page(request:Request, db: Session = Depends(get_db)):
        stmnt = db.select(Customer)
        users:list = db.session.scalars(stmnt).all()
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