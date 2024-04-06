from pydantic import BaseModel

class ItemCreateSchema(BaseModel):
    name: str
    description: str
    image: int
    category: str
    price: float
    quantity: int
    
class ItemUpdateSchema(ItemCreateSchema):
    pass
    