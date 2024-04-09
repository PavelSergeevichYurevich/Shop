from pydantic import BaseModel

class OrderItem(BaseModel):
    item_id: int
    quantity: int