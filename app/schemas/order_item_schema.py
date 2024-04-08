from pydantic import BaseModel

class OrderItem(BaseModel):
    item_in_order_id: int
    quantity_in_order: int