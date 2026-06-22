import random
import time
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware

# Import schemas, database tools, models, and analytics engines
from app.schemas import SearchResponse, ProductResult, SearchQueryInput
from app.database import engine, Base, get_db
from app.models import ProductPriceHistory
from app.scraper import scrape_live_platform
from app.analytics import get_price_trends
from app.predictor import predict_future_price

app = FastAPI(title="Quick-Commerce Price Aggregator API - Custom Links Synced")

# ------------------------------------------------------------------
# SECURITY LAYER: CORS COMPLIANCE CONFIGURATION
# ------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# PERFORMANCE LAYER: IN-MEMORY CACHE STORAGE
# ------------------------------------------------------------------
SEARCH_CACHE = {}
CACHE_TTL_MINUTES = 5  

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[DATABASE] Physical tables synced successfully.")

# ------------------------------------------------------------------
# PERFORMANCE LAYER: LIVE DIAGNOSTICS MIDDLEWARE
# ------------------------------------------------------------------
@app.middleware("http")
async def add_performance_diagnostics_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Inject latency stats directly into response headers for frontend tracking
    response.headers["X-Process-Time-Ms"] = f"{round(process_time, 2)}"
    return response

# ------------------------------------------------------------------
# DEEP-LINK SIMULATION LAYER (EXACT LINK OVERRIDES)
# ------------------------------------------------------------------
def simulate_platform_scraper(query: str, platform_name: str, base_price: float):
    q_low = query.lower()
    
    # Establish realistic randomized variations for pricing metrics
    platform_modifier = {
        "Blinkit": random.uniform(-2.0, 1.5),
        "Zepto": random.uniform(-1.0, 2.5),
        "Swiggy Instamart": random.uniform(-3.0, 0.5)
    }
    final_price = round(base_price + platform_modifier.get(platform_name, 0.0), 2)
    
    # Set default structural fallbacks
    title = f"{query.capitalize()} Premium Fresh Pack"
    quantity = "500g" if "milk" not in q_low else "500 ml"
    product_url = f"https://{platform_name.lower().replace(' ', '')}.com"

    # Exact Mapping for Sample Item: MAGGI
    if "maggi" in q_low:
        title = "Maggi Double Masala Instant Noodles"
        quantity = "70g"
        if platform_name == "Zepto":
            product_url = "https://www.zepto.com/pn/maggi-double-masala-instant-noodles/pvid/c5203619-7189-4476-bfcd-59b55ed50682"
        elif platform_name == "Blinkit":
            product_url = "https://blinkit.com/prn/maggi-double-masala-instant-noodles/prid/699111"
        elif platform_name == "Swiggy Instamart":
            product_url = "https://www.swiggy.com/instamart/item/LLCA5UP70U"

    # Exact Mapping for Sample Item: MILK
    elif "milk" in q_low:
        title = "Amul Moti Toned Milk" if platform_name == "Zepto" else "Amul Taaza Toned Milk"
        quantity = "500 ml"
        if platform_name == "Zepto":
            product_url = "https://www.zepto.com/pn/amul-moti-toned-milk-90-days-shelf-life/pvid/1638f685-befc-478e-95f8-2d92213866e7"
        elif platform_name == "Blinkit":
            product_url = "https://blinkit.com/prn/amul-taaza-toned-milk/prid/19512"
        elif platform_name == "Swiggy Instamart":
            product_url = "https://www.swiggy.com/instamart/item/JKFJW8ZUYW"

    return ProductResult(
        title=title,
        platform=platform_name,
        price=final_price,
        quantity=quantity,
        image_url=f"https://via.placeholder.com/150?text={platform_name}",
        product_url=product_url
    )

# ------------------------------------------------------------------
# ROUTING LAYER: HARDENED & CACHED CORE SEARCH ENDPOINT
# ------------------------------------------------------------------
@app.get("/api/v1/search", response_model=SearchResponse)
async def search_products(query: str, db: AsyncSession = Depends(get_db)):
    try:
        validated_input = SearchQueryInput(query=query)
        clean_query = validated_input.query.strip().lower()
    except Exception:
        raise HTTPException(
            status_code=400, 
            detail="Security Alert: Search query contains prohibited characters or violates length parameters."
        )

    query_key = clean_query
    current_time = datetime.utcnow()
    
    if query_key in SEARCH_CACHE:
        cache_entry = SEARCH_CACHE[query_key]
        if current_time - cache_entry["timestamp"] < timedelta(minutes=CACHE_TTL_MINUTES):
            print(f"[CACHE HIT] Serving results for '{query_key}' directly from memory.")
            return cache_entry["data"]

    print(f"[CACHE MISS] Executing scraping pipeline for '{query_key}'.")
    platforms = ["Blinkit", "Zepto", "Swiggy Instamart"]
    aggregated_results = []
    
    for platform in platforms:
        live_items = await scrape_live_platform(clean_query, platform)
        
        if not live_items:
            base_market_price = 20.0 if "maggi" in clean_query else 33.0 if "milk" in clean_query else 45.0
            fallback_item = simulate_platform_scraper(clean_query, platform, base_market_price)
            live_items = [fallback_item]
            
        for scraped_item in live_items:
            aggregated_results.append(scraped_item)
            
            history_entry = ProductPriceHistory(
                query_term=clean_query,
                platform=scraped_item.platform,
                title=scraped_item.title,
                price=scraped_item.price,
                quantity=scraped_item.quantity
            )
            db.add(history_entry)
            
    await db.commit()
    sorted_results = sorted(aggregated_results, key=lambda item: item.price)
    
    response_data = SearchResponse(search_query=clean_query, results=sorted_results)
    SEARCH_CACHE[query_key] = {
        "timestamp": current_time,
        "data": response_data
    }
    
    return response_data

# ------------------------------------------------------------------
# ROUTING LAYER: DATA SCIENCE TREND ANALYTICS ENDPOINT
# ------------------------------------------------------------------
@app.get("/api/v1/analytics/trends")
async def get_item_analytics(query: str, db: AsyncSession = Depends(get_db)):
    trends = await get_price_trends(query, db)
    return trends

# ------------------------------------------------------------------
# ROUTING LAYER: PREDICTIVE PRICE ENGINE ENDPOINT
# ------------------------------------------------------------------
@app.get("/api/v1/predict/price")
async def get_price_prediction(query: str, platform: str, db: AsyncSession = Depends(get_db)):
    prediction = await predict_future_price(query, platform, db)
    return prediction

@app.get("/")
def home():
    return {"message": "Welcome to the Grocery Price Comparator API! Append /docs to the URL to view interactive documentation."}