from pydantic import BaseModel

class CustomerCreateSchema(BaseModel):
    email: str
    password: str
    name: str
    
class CustomerUpdateSchema(CustomerCreateSchema):
    role: str
    