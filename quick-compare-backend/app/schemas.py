from pydantic import BaseModel #class used to create structured data models that automatically validate incoming and outgoing data types
from typing import Optional, List #Optional allows fields to be empty (None), and List allows a variable to hold an array of items

class ProductResult(BaseModel):
    title: str #product name 
    platform: str #3 options zepto,blinkit,instarmart 
    price: float
    quantity: str
    image_url: Optional[str] = None  #craper fails to find an image, this field defaults gracefully to None without crashing our app
    product_url: Optional[str] = None

class SearchResponse(BaseModel):  #SearchResponse to layout what our final search API endpoint returns to the frontend user interface
    search_query: str
    results: List[ProductResult]