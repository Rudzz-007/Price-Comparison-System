from pydantic import BaseModel, Field
from typing import Optional, List

class ProductResult(BaseModel):
    title: str 
    platform: str 
    price: float
    quantity: str
    image_url: Optional[str] = None  
    product_url: Optional[str] = None

class SearchResponse(BaseModel):  
    search_query: str
    results: List[ProductResult]

# New Input Validation Schema to prevent SQL Injection / XSS payloads
class SearchQueryInput(BaseModel):
    query: str = Field(..., min_length=2, max_length=50, pattern=r"^[a-zA-Z0-9\s\-\(\)]+$")