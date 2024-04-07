# from models.order_model import Order
from models.order_model import Order
from database.database import Base
from datetime import datetime
from typing import List
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str]
    password: Mapped[str]
    name: Mapped[str]
    data_create: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    data_change: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    role: Mapped[str] = mapped_column(default='user')
    orders: Mapped[List["Order"]] = relationship(back_populates='customer', cascade='save-update, merge, delete')