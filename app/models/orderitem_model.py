from database.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
        
class OrderItem(Base):
    __tablename__ = 'order_items'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'))
    item_id: Mapped[str] = mapped_column(ForeignKey('items.id'))
    quantity: Mapped[int]
    item: Mapped[str] = relationship('Item')
    order: Mapped[str] = relationship('Order')
