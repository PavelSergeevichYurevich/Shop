from database.database import Base
from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Order(Base):
    __tablename__ = "order"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    data_create: Mapped[datetime]
    status: Mapped[str]
    customer_id: Mapped[str] = mapped_column(ForeignKey('customer.id'))
    line_items: Mapped[List["OrderItem"]] = relationship(back_populates='order', cascade='save-update, merge, delete')