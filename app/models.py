from database import Base
from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str]
    password: Mapped[str]
    data_create: Mapped[datetime]
    data_change: Mapped[datetime]
    role: Mapped[str]
    orders: Mapped[List["Order"]] = relationship(back_populates='customer', cascade='save-update, merge, delete')
        
class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    data_create: Mapped[datetime]
    status: Mapped[str]
    customer_id: Mapped[str] = mapped_column(ForeignKey('customers.id'))
    line_items: Mapped[List["OrderItem"]] = relationship(back_populates='order', cascade='save-update, merge, delete')

class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]
    description: Mapped[str]
    image: Mapped[int]
    data_create: Mapped[datetime]
    data_change: Mapped[datetime]
    category: Mapped[str]
    price: Mapped[int]
    quantity: Mapped[int]

class OrderItem(Base):
    __tablename__ = 'order_items'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'))
    item_id: Mapped[str] = mapped_column(ForeignKey('items.id'))
    quantity: Mapped[int]
    item: Mapped[str] = relationship('Item')



