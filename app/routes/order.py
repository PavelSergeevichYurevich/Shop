from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.dependencies.dependency import get_db
from app.models.models import Order, OrderItem, Item
from app.schemas.schemas import AddingItemSchema, DeletingItemSchema, OrderCreateSchema, OrderItemSchema, UpdatingItemSchema

order_router = APIRouter(prefix='/order', tags=['Orders'])

@order_router.get("/show/{customer_id}")
def get_customer_orders(customer_id: int, db: Session = Depends(get_db)):
    orders = db.scalars(select(Order).where(Order.customer_id == customer_id)).all()
    return orders

@order_router.post("/add/", status_code=status.HTTP_201_CREATED)
def add_order(order_data: OrderCreateSchema, items_data: List[OrderItemSchema], db: Session = Depends(get_db)):
    if not items_data:
        raise HTTPException(400, 'Список товаров пуст')
    # 1. Начинаем транзакцию (в SQLAlchemy 2.0 она начинается автоматически при работе с сессией)
    try:
        # Создаем "голову" заказа
        new_order = Order(
            customer_id=order_data.customer_id, 
            status="pending" # Стандарт 2026: начальный статус всегда через код или БД
        )
        db.add(new_order)
        db.flush() # Получаем ID заказа, не фиксируя изменения в БД (без commit)

        for item_info in items_data:
            # 2. Проверяем наличие товара и фиксируем цену (Snapshot)
            db_item = db.get(Item, item_info.item_id)
            if not db_item:
                raise HTTPException(status_code=404, detail=f"Товар {item_info.item_id} не найден")
            
            if db_item.quantity < item_info.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Недостаточно товара {db_item.name} на складе. В наличии: {db_item.quantity}"
                )

            # 3. Списываем остаток (Бизнес-логика)
            db_item.quantity -= item_info.quantity
            
            # 4. Создаем строку заказа с фиксацией цены
            new_order_item = OrderItem(
                order_id=new_order.id,
                item_id=db_item.id,
                quantity=item_info.quantity,
                price_at_purchase=db_item.price # Навык: защита от изменения цен в будущем
            )
            db.add(new_order_item)

        # 5. Один финальный коммит для всей операции
        db.commit()
        db.refresh(new_order)
        return new_order

    except Exception as e:
        db.rollback() # Если хоть что-то пошло не так — отменяем всё!
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail="Ошибка при создании заказа")


# Удалить заказ (с возвратом товара на склад)
@order_router.delete('/delete/{id}')
def del_order(id: int, db: Session = Depends(get_db)):
    order = db.get(Order, id)
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    items_in_order = db.scalars(select(OrderItem).where(OrderItem.order_id == id)).all()
    
    for entry in items_in_order:
        item = db.get(Item, entry.item_id)
        if item:
            item.quantity += entry.quantity # Возвращаем товар на склад     
    db.delete(order)
    db.commit()
    return {"status": "deleted", "id": id}

@order_router.put('/update/')
def update_order_item(updating_item: UpdatingItemSchema, db: Session = Depends(get_db)):
    # 1. Находим текущую строку в заказе (используем кортеж для составного ключа)
    order_item = db.get(OrderItem, (updating_item.order_id, updating_item.item_id))
    
    if not order_item:
        raise HTTPException(status_code=404, detail="Позиция в заказе не найдена")

    # 2. Находим товар на складе
    item = db.get(Item, order_item.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Товар не найден на складе")

    # 3. Считаем разницу (Delta)
    # Если new > old: разница положительная (нужно еще списать со склада)
    # Если new < old: разница отрицательная (нужно вернуть на склад)
    diff = updating_item.new_quantity - order_item.quantity

    # 4. Проверяем склад, если количество увеличивается
    if diff > 0 and item.quantity < diff:
        raise HTTPException(
            status_code=400, 
            detail=f"Недостаточно товара на складе. Можно добавить еще: {item.quantity}"
        )

    # 5. Обновляем склад и строку заказа
    item.quantity -= diff # Если diff отрицательный, минус на минус даст плюс (возврат)
    order_item.quantity = updating_item.new_quantity

    db.commit()
    db.refresh(order_item)
    return order_item

#удалить строку в заказе
@order_router.delete(path='/deleteitem/')
async def del_item(deleting_item: DeletingItemSchema, db: Session = Depends(get_db)):
    # 1. Находим конкретную строку в заказе. 
    # Так как ключ составной, передаем кортеж (order_id, item_id)
    order_item = db.get(OrderItem, (deleting_item.order_id, deleting_item.item_id))
    if not order_item:
        raise HTTPException(status_code=404, detail="Строка в заказе не найдена")
    # 2. Находим сам товар на складе
    item = db.get(Item, order_item.item_id)
    if item:
        item.quantity += order_item.quantity 
    db.delete(order_item)
    db.commit()
    return {"status": "success", "message": "Товар возвращен на склад, строка удалена"}


# Добавить строку в заказ (с фиксацией цены и списанием со склада)
@order_router.post('/additem/')
def add_item_to_order(adding_item: AddingItemSchema, db: Session = Depends(get_db)):
    # 1. Проверяем товар и наличие
    db_item = db.get(Item, adding_item.item_id)
    if not db_item or db_item.quantity < adding_item.quantity:
        raise HTTPException(status_code=400, detail="Товар недоступен или недостаточно на складе")
    db_item.quantity -= adding_item.quantity
    
    new_order_item = OrderItem(
        order_id = adding_item.order_id,
        item_id = adding_item.item_id,
        quantity = adding_item.quantity,
        price_at_purchase = db_item.price # Snapshot Pricing!
    )
    db.add(new_order_item)
    db.commit()
    db.refresh(new_order_item)
    return new_order_item



    
