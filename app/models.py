from database import Base
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    password: Mapped[str]
    data_create: Mapped[str]
    data_change: Mapped[str]
    role: Mapped[str]
    orders: Mapped[List["Order"]] = relationship(back_populates='user', cascade='save-update, merge, delete')
        
class Order(Base):
    __tablename__ = "order"
    id: Mapped[int] = mapped_column(primary_key=True)
    data_create: Mapped[str]
    status: Mapped[str]
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id'))
    user: Mapped["User"] = relationship(back_populates="orders")
    products: Mapped[List["Product"]] = relationship(back_populates='order', cascade='save-update, merge, delete')

class Product(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    image: Mapped[image]
    data_create: Mapped[str]
    data_change: Mapped[str]
    category: Mapped[str]
    price: Mapped[int]
    quantity: Mapped[int]
    order: Mapped["Order"]