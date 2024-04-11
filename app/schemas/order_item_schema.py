from pydantic import BaseModel

class OrderItemSchema(BaseModel):
    item_id: int
    quantity: int