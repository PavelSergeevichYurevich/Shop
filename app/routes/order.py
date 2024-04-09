# роутер операция с заказами
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session
from models.orderitem_model import OrderItem
from dependencies.dependency import get_db
from models.order_model import Order
from schemas.order_schema import OrderCreateSchema

order_router = APIRouter(
    prefix='/order',
    tags=['Orders']
)
templates = Jinja2Templates(directory="templates")

@order_router.get("/show/")
async def get_items(request:Request, db: Session = Depends(get_db)):
    stmnt = select(Order).where(Order.customer_id == 2)
    orders:list = db.scalars(stmnt).all()
    """  context:dict = {}
    i:int = 1
    for item in items:
        new_el = {str(i): item.name}
        context.update(new_el)
        i += 1
    return templates.TemplateResponse("users.html", {"request": request, "context": context}) """
    return orders

# создать заказ
@order_router.post("/add/")
async def add_order(request:Request,  customer_id: int, status: str, order: OrderCreateSchema, db: Session = Depends(get_db)):
    new_order = Order(
        customer_id = customer_id, 
        status = status,
        item = [dict(x) for x in order]
        )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    # return RedirectResponse(url="/app/login/", status_code=status.HTTP_302_FOUND)
    return new_order

