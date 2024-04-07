from database.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
        
class OrderItem(Base):
    __tablename__ = 'order_items'
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), primary_key=True)
    item_id: Mapped[str] = mapped_column(ForeignKey('items.id'), primary_key=True)
    quantity: Mapped[int]
    item: Mapped[str] = relationship('Item', back_populates='orders')
    order: Mapped[str] = relationship('Order', back_populates='item')
