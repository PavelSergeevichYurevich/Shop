from pydantic import BaseModel

class OrderCreateSchema(BaseModel):
    customer_id: int
    status: str
    
