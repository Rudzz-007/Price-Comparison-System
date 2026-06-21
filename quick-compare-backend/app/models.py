from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base

class ProductPriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    query_term = Column(String, index=True)
    platform = Column(String, index=True)
    title = Column(String)
    price = Column(Float)
    quantity = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)