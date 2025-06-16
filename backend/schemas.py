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
    # --- PHASE 2 ADDITION ---
    master_pattern_path: Optional[str] = None

class VerificationResponse(BaseModel):
    status: str
    message: str
    similarity_score: Optional[float] = None
    product_data: Optional[Product] = None