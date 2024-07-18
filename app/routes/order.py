# роутер операция с заказами
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session
from models.models import OrderItem
from dependencies.dependency import get_db
from models.models import Order
from schemas.schemas import AddingItemSchema, DeletingItemSchema, OrderCreateSchema, OrderItemSchema, UpdatingItemSchema


order_router = APIRouter(
    prefix='/order',
    tags=['Orders']
)
templates = Jinja2Templates(directory="templates")

@order_router.get("/show/")
async def get_items(request:Request, customer_id:int, db: Session = Depends(get_db)):
    stmnt = select(Order).where(Order.customer_id == customer_id)
    orders:list = db.scalars(stmnt).all()
    for order in orders:
        print(order.item)
    return orders

# создать заказ
@order_router.post("/add/")
async def add_order(request:Request, order: OrderCreateSchema, order_item: List[OrderItemSchema], db: Session = Depends(get_db)):
    new_order = Order(
        customer_id = order.customer_id, 
        status = order.status,
        )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    for item in order_item:
        new_order_item = OrderItem(
            order_id = new_order.id,
            item_id = item.item_id,
            quantity = item.quantity
        )
        db.add(new_order_item)
        db.commit()
        db.refresh(new_order_item)
    # return RedirectResponse(url="/app/login/", status_code=status.HTTP_302_FOUND)
    return new_order

# удалить заказ
@order_router.delete(path='/delete/')
async def del_order(request:Request, id:int, db: Session = Depends(get_db)):
    stmnt = delete(Order).where(Order.id == id)
    order = db.execute(stmnt)
    db.commit()
    return order

#изменить заказ
@order_router.put(path='/update/')
async def update_order(request:Request, updating_item: UpdatingItemSchema, db: Session = Depends(get_db)):
    stmnt = update(OrderItem).where((OrderItem.order_id == updating_item.order_id) & (OrderItem.item_id == updating_item.item_id)).values(
        quantity = updating_item.new_quantity
    )
    updated_item = db.execute(stmnt)
    db.commit()
    return updated_item

#удалить строку в заказе
@order_router.delete(path='/deleteitem/')
async def del_item(request:Request, deleting_item: DeletingItemSchema,db: Session = Depends(get_db)):
    stmnt = delete(OrderItem).where((OrderItem.order_id == deleting_item.order_id ) & (OrderItem.item_id == deleting_item.item_id))
    deleted_item = db.execute(stmnt)
    db.commit()
    return deleted_item

#добавить строку в заказ
@order_router.post(path='/additem/')
async def add_item(request:Request, adding_item: AddingItemSchema,db: Session = Depends(get_db)):
    new_order_item = OrderItem(
        order_id = adding_item.order_id,
        item_id = adding_item.item_id,
        quantity = adding_item.quantity
    )
    db.add(new_order_item)
    db.commit()
    db.refresh(new_order_item)
    return new_order_item



    
