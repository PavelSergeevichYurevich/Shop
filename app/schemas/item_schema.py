from pydantic import BaseModel

class ItemCreateSchema(BaseModel):
    email: str
    password: str
    name: str
    
class ItemUpdateSchema(BaseModel):
    id: int
    field: str
    new_value: str
    name: str
    
class ItemDeleteSchema(BaseModel):
    id: int