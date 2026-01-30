from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from app.routes.auth import get_current_admin, get_current_user, hashing_pass
from app.dependencies.dependency import get_db
from app.models.models import Customer
from app.schemas.schemas import CustomerCreateSchema, CustomerUpdateSchema, CustomerReadSchema


customer_router = APIRouter(
    prefix='/customer',
    tags=['Customers']
)
# вывести пользoвателей
@customer_router.get("/show/", response_model=List[CustomerReadSchema])
def get_customers(db: Session = Depends(get_db)):
    users = db.scalars(select(Customer)).all()
    return users

# Регистрация покупателя
@customer_router.post("/register/", response_model=CustomerReadSchema)
def add_customer(customer: CustomerCreateSchema, db: Session = Depends(get_db)):
    # Проверка на дубликат email
    existing_user = db.scalar(select(Customer).where(Customer.email == customer.email))
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    new_customer = Customer(
        email=customer.email,
        hashed_password=hashing_pass(customer.password), # Пароль берем из схемы
        name=customer.name,
        role="user" 
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

# Обновление профиля
@customer_router.put('/update/{customer_id}', response_model=CustomerReadSchema)
def update_customer(
    customer_id: int, 
    customer_upd: CustomerUpdateSchema, 
    current_user: Customer = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    db_customer = db.get(Customer, customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if current_user.role != "admin" and current_user.id != customer_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    update_data = customer_upd.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if key == 'role':
            # Проверяем роль ТОЛЬКО если её пытаются изменить
            if value != db_customer.role and current_user.role != "admin":
                raise HTTPException(status_code=403, detail="Только админ может менять роли")
        
        if key == 'password':
            setattr(db_customer, 'hashed_password', hashing_pass(value))
        else:
            setattr(db_customer, key, value)

    db.commit()
    db.refresh(db_customer)
    return db_customer

# удалить пользователя
@customer_router.delete(path='/delete/')
async def del_customer(id:int, db: Session = Depends(get_db)):
    stmnt = delete(Customer).where(Customer.id == id)
    customer = db.execute(stmnt)
    db.commit()
    return customer