from pydantic import BaseModel

class CustomerCreateSchema(BaseModel):
    email: str
    password: str
    name: str
    
class CustomerUpdateSchema(BaseModel):
    id: int
    field: str
    new_value: str
    name: str
    
class CustomerDeleteSchema(BaseModel):
    id: int