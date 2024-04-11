# роутер операция с товарами
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session
from dependencies.dependency import get_db
from models.models import Item
from schemas.schemas import ItemCreateSchema, ItemUpdateSchema

item_router = APIRouter(
    prefix='/item',
    tags=['Items']
)
templates = Jinja2Templates(directory="templates")

# вывести товары
@item_router.get("/show/", response_model=List[ItemCreateSchema])
async def get_items(request:Request, db: Session = Depends(get_db)):
    stmnt = select(Item)
    items:list = db.scalars(stmnt).all()
    """  context:dict = {}
    i:int = 1
    for item in items:
        new_el = {str(i): item.name}
        context.update(new_el)
        i += 1
    return templates.TemplateResponse("users.html", {"request": request, "context": context}) """
    return items

# создать товары
@item_router.post("/add/", response_model=ItemCreateSchema)
async def add_item(request:Request, item: ItemCreateSchema, db: Session = Depends(get_db)):
    new_item = Item(
        name = item.name,
        description = item.description,
        image = item.image,
        category = item.category,
        price = item.price,
        quantity = item.quantity
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    # return RedirectResponse(url="/app/login/", status_code=status.HTTP_302_FOUND)
    return new_item

# изменить товары
@item_router.put(path='/update/')
async def change_item(request:Request, item_id:int, item_upd: ItemUpdateSchema, db: Session = Depends(get_db)):
    stmnt = update(Item).where(Item.id == item_id).values(
        name = item_upd.name,
        description = item_upd.description,
        image = item_upd.image,
        category = item_upd.category,
        price = item_upd.price,
        quantity = item_upd.quantity,
        data_change = datetime.utcnow()
    )
    item = db.execute(stmnt)
    db.commit()
    return item

# удалить товары
@item_router.delete(path='/delete/')
async def del_item(request:Request, id:int, db: Session = Depends(get_db)):
    stmnt = delete(Item).where(Item.id == id)
    customer = db.execute(stmnt)
    db.commit()
    return customer