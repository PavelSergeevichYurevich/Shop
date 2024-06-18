from pydantic import BaseModel

class CustomerCreateSchema(BaseModel):
    email: str
    password: str
    name: str
    
class CustomerUpdateSchema(CustomerCreateSchema):
    role: str
    
class OrderCreateSchema(BaseModel):
    customer_id: int
    status: str
    
class ItemCreateSchema(BaseModel):
    name: str
    description: str
    image: int
    category: str
    price: float
    quantity: int
    
class ItemUpdateSchema(ItemCreateSchema):
    pass

class OrderItemSchema(BaseModel):
    item_id: int
    quantity: int
    
class DeletingItemSchema(BaseModel):
    order_id: int
    item_id: int