from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import ForeignKey, Numeric, String, text
from decimal import Decimal
from app.database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Customer(Base):
    __tablename__ = "customer"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str]
    name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(server_default='user') # Изменяем на server_default
    created_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.now(timezone.utc))
    orders: Mapped[List["Order"]] = relationship(back_populates='customer', cascade='all, delete-orphan')
    refresh_tokens: Mapped[List['RefreshTokens']] = relationship(back_populates='user', cascade='all, delete-orphan')

class Item(Base):
    __tablename__ = "item"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(1000))
    image: Mapped[Optional[str]]
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2)) # Храним деньги правильно
    quantity: Mapped[int] = mapped_column(default=0)
    category: Mapped[str] = mapped_column(index=True) # Добавим индекс для поиска по категориям
    order_items: Mapped[List['OrderItem']] = relationship(back_populates='item')

        
class Order(Base):
    __tablename__ = "order"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    status: Mapped[str] = mapped_column(default="pending") # Ожидает оплаты, в пути и т.д.
    customer_id: Mapped[int] = mapped_column(ForeignKey('customer.id', ondelete='CASCADE'), index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))
    customer: Mapped["Customer"] = relationship(back_populates='orders')
    items: Mapped[List["OrderItem"]] = relationship(back_populates='order', cascade='all, delete-orphan')

class OrderItem(Base):
    __tablename__ = 'order_item'
    order_id: Mapped[int] = mapped_column(ForeignKey('order.id', ondelete='CASCADE'), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey('item.id', ondelete='CASCADE'), primary_key=True)
    quantity: Mapped[int]
    price_at_purchase: Mapped[Decimal] = mapped_column(Numeric(10, 2)) # ФИКСИРУЕМ цену на момент покупки!
    item: Mapped["Item"] = relationship(back_populates='order_items')
    order: Mapped["Order"] = relationship(back_populates='items')
    
class RefreshTokens(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('customer.id', ondelete='CASCADE'), index=True)
    token_hash: Mapped[str] = mapped_column(String(255))
    expires_at: Mapped[datetime] = mapped_column()
    revoked: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))
    user: Mapped['Customer'] = relationship(back_populates='refresh_tokens')
    
    
    
    
    
    
    