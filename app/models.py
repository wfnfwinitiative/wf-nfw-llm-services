from pydantic import BaseModel, Field
from typing import List, Optional

class FoodItem(BaseModel):
    foodName: Optional[str] = None
    quantity: Optional[str] = None
    quality: Optional[str] = None

class FoodMetadata(BaseModel):
    items: List[FoodItem] = Field(default_factory=list)
