from pydantic import BaseModel
from typing import Optional

class ProductCreate(BaseModel):
    product_name: str
    company_name: str

class Product(BaseModel):
    id: int
    unique_id: str
    product_name: str
    company_name: str

class VerificationResponse(BaseModel):
    status: str
    message: str
    product_data: Optional[Product] = None