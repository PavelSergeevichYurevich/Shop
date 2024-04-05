from database.database import Base
from datetime import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

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
    