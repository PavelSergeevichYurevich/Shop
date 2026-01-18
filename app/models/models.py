from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey
from app.database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Customer(Base):
    __tablename__ = "customer"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str]
    hashed_password: Mapped[str]
    name: Mapped[str]
    data_create: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    data_change: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    role: Mapped[str] = mapped_column(default='user')
    order: Mapped[List["Order"]] = relationship(back_populates='customer', cascade='save-update, merge, delete', passive_deletes=True)
    

class Item(Base):
    __tablename__ = "item"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]
    description: Mapped[str]
    image: Mapped[Optional[str]]
    data_create: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    data_change: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    category: Mapped[str]
    price: Mapped[float]
    quantity: Mapped[int]
    orders: Mapped[List['OrderItem']] = relationship(back_populates='item')
    
    
class Order(Base):
    __tablename__ = "order"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date_create: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    date_change: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    status: Mapped[str]
    customer_id: Mapped[int] = mapped_column(ForeignKey('customer.id', ondelete='CASCADE'), index=True)
    item: Mapped[List["OrderItem"]] = relationship(back_populates='order', cascade='save-update, merge, delete', passive_deletes=True)
    customer: Mapped["Customer"] = relationship(back_populates='order')

class OrderItem(Base):
    __tablename__ = 'order_item'
    order_id: Mapped[int] = mapped_column(ForeignKey('order.id', ondelete='CASCADE'), index=True, primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey('item.id'), primary_key=True)
    quantity: Mapped[int]
    item: Mapped[str] = relationship('Item', back_populates='orders')
    order: Mapped[str] = relationship('Order', back_populates='item')
    
    
    
    
    
    
    
    
    