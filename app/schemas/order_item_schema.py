from typing import Dict
from pydantic import BaseModel

class OrderItem(BaseModel):
    order: Dict[int, int]