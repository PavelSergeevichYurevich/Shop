from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr

# --- Схемы Пользователя ---
class CustomerBase(BaseModel):
    email: EmailStr # Валидация корректности почты
    name: str = Field(..., min_length=2, max_length=100)

class CustomerCreateSchema(CustomerBase):
    password: str = Field(..., min_length=6) # Принимаем чистый пароль
    
class CustomerUpdateSchema(BaseModel):
    # Все поля Optional, чтобы можно было обновить только что-то одно
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6) # Для смены пароля
    role: Optional[str] = None # Только для админа

class CustomerReadSchema(CustomerBase):
    id: int
    role: str
    model_config = ConfigDict(from_attributes=True) # Для связи с SQLAlchemy

# --- Схемы Товаров ---
class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., max_length=1000)
    category: str
    price: Decimal = Field(..., gt=0) # Цена строго больше 0
    quantity: int = Field(..., ge=0) # Количество не меньше 0

class ItemCreateSchema(ItemBase):
    image: Optional[str] = None

class ItemUpdateSchema(BaseModel):
    # Позволяет обновлять поля по отдельности
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)
    image: Optional[str] = None

# --- Схемы Заказов ---
class OrderItemSchema(BaseModel):
    item_id: int
    quantity: int = Field(..., gt=0)

class OrderCreateSchema(BaseModel):
    customer_id: int
    status: str = "pending"

class AddingItemSchema(OrderItemSchema):
    order_id: int

class DeletingItemSchema(BaseModel):
    order_id: int
    item_id: int

class UpdatingItemSchema(DeletingItemSchema):
    new_quantity: int = Field(..., gt=0)
