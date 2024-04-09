from typing import List
from pydantic import BaseModel

from schemas.order_item_schema import OrderItem

class OrderCreateSchema(BaseModel):
    item: List['OrderItem'] = []
    class Config:
        from_attributes = True
