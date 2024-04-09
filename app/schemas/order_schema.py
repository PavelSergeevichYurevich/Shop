from typing import Dict, List
from pydantic import BaseModel

from schemas.order_item_schema import OrderItem

class OrderCreateSchema(BaseModel):
    customer_id: int
    status: str
    item: list[OrderItem]
    """ class Config:
        from_attributes = True """
