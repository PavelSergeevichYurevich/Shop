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
    data_create: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    data_change: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    category: Mapped[str]
    price: Mapped[float]
    quantity: Mapped[int]
    