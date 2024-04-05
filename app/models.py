from database.database import Base
from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Customer(Base):
    __tablename__ = "customer"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str]
    password: Mapped[str]
    data_create: Mapped[datetime]
    data_change: Mapped[datetime]
    role: Mapped[str] = mapped_column(default='user')
    orders: Mapped[List["Order"]] = relationship(back_populates='customer', cascade='save-update, merge, delete')
        
class Order(Base):
    __tablename__ = "order"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    data_create: Mapped[datetime]
    status: Mapped[str]
    customer_id: Mapped[str] = mapped_column(ForeignKey('customer.id'))
    line_items: Mapped[List["OrderItem"]] = relationship(back_populates='order', cascade='save-update, merge, delete')

class Item(Base):
    __tablename__ = "item"
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
    __tablename__ = 'order_item'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('order.id'))
    item_id: Mapped[str] = mapped_column(ForeignKey('item.id'))
    quantity: Mapped[int]
    item: Mapped[str] = relationship('Item')



