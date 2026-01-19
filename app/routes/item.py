import os
import uuid
import aiofiles
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from dependencies.dependency import get_db
from app.models.models import Item
from schemas.schemas import ItemCreateSchema, ItemUpdateSchema

item_router = APIRouter(prefix='/item', tags=['Items'])

IMAGES_DIR = "static/images"

# Показать товары
@item_router.get("/show/", response_model=List[ItemCreateSchema])
def get_items(db: Session = Depends(get_db)):
    items = db.scalars(select(Item)).all()
    return items

# Создать товар
@item_router.post("/add/", status_code=status.HTTP_201_CREATED)
async def add_item(
    item: ItemCreateSchema = Depends(), 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    
    os.makedirs(IMAGES_DIR, exist_ok=True)
    
   
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    image_path = os.path.join(IMAGES_DIR, unique_filename)
    
    
    async with aiofiles.open(image_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
        
    new_item = Item(
        name=item.name,
        description=item.description,
        image=image_path,
        category=item.category,
        price=item.price,
        quantity=item.quantity
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

# Удалить товар
@item_router.delete('/delete/{item_id}')
def del_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    # Удаляем физический файл изображения, если он есть
    if item.image and os.path.exists(item.image):
        os.remove(item.image)
        
    db.delete(item)
    db.commit()
    return {"message": f"Товар {item_id} успешно удален"}
