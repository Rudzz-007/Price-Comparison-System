import random
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import SearchResponse, ProductResult
from app.database import engine, Base, get_db
from app.models import ProductPriceHistory
from app.scraper import scrape_live_platform
from fastapi.middleware.cors import CORSMiddleware

# Import your analytics and machine learning engines
from app.analytics import get_price_trends
from app.predictor import predict_future_price

app = FastAPI(title="Quick-Commerce Price Aggregator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[DATABASE] Physical tables synced successfully.")

def simulate_platform_scraper(query: str, platform_name: str, base_price: float):
    platform_modifier = {
        "Blinkit": random.uniform(-2.0, 1.5),
        "Zepto": random.uniform(-1.0, 2.5),
        "Swiggy Instamart": random.uniform(-3.0, 0.5)
    }
    final_price = round(base_price + platform_modifier.get(platform_name, 0.0), 2)
    return ProductResult(
        title=f"{query.capitalize()} Premium Fresh Pack",
        platform=platform_name,
        price=final_price,
        quantity="500g" if "milk" not in query.lower() else "500 ml",
        image_url=f"https://via.placeholder.com/150?text={platform_name}",
        product_url=f"https://{platform_name.lower().replace(' ', '')}.com/mock-{query}"
    )

# 1. Core Live Search Aggregator
@app.get("/api/v1/search", response_model=SearchResponse)
async def search_products(query: str, db: AsyncSession = Depends(get_db)):
    platforms = ["Blinkit", "Zepto", "Swiggy Instamart"]
    aggregated_results = []
    
    for platform in platforms:
        live_items = await scrape_live_platform(query, platform)
        
        if not live_items:
            base_market_price = 14.0 if "maggi" in query.lower() else 33.0 if "milk" in query.lower() else 45.0
            fallback_item = simulate_platform_scraper(query, platform, base_market_price)
            live_items = [fallback_item]
            
        for scraped_item in live_items:
            aggregated_results.append(scraped_item)
            
            history_entry = ProductPriceHistory(
                query_term=query,
                platform=scraped_item.platform,
                title=scraped_item.title,
                price=scraped_item.price,
                quantity=scraped_item.quantity
            )
            db.add(history_entry)
            
    await db.commit()
    sorted_results = sorted(aggregated_results, key=lambda item: item.price)
    return SearchResponse(search_query=query, results=sorted_results)

# 2. ADDED: Data Science Analytics Endpoint
@app.get("/api/v1/analytics/trends")
async def get_item_analytics(query: str, db: AsyncSession = Depends(get_db)):
    trends = await get_price_trends(query, db)
    return trends

# 3. ADDED: Exponential Moving Average Prediction Forecasting Endpoint
@app.get("/api/v1/predict/price")
async def get_price_prediction(query: str, platform: str, db: AsyncSession = Depends(get_db)):
    prediction = await predict_future_price(query, platform, db)
    return prediction

@app.get("/")
def home():
    return {"message": "Welcome to the Grocery Price Comparator API! Append /docs to the URL to view interactive documentation."}