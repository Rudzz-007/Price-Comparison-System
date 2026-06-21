from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import ProductPriceHistory

async def predict_future_price(query_term: str, platform_name: str, db: AsyncSession, days_ahead: int = 7):
    """
    Applies an Exponential Moving Average (EMA) smoothing model to historical 
    price trends and projects a realistic future boundary.
    """
    # 1. Fetch chronological pricing data entries
    stmt = select(ProductPriceHistory.price).where(
        ProductPriceHistory.query_term.ilike(f"%{query_term}%"),
        ProductPriceHistory.platform == platform_name
    ).order_by(ProductPriceHistory.timestamp.asc())
    
    result = await db.execute(stmt)
    prices = [row[0] for row in result.all()]
    
    n = len(prices)
    if n < 3:
        return {"error": f"Insufficient dataset matrix size ({n} entries) to compute smooth averages."}
        
    # 2. Calculate the core smoothing factor (alpha)
    # Standard alpha weight allocation for an EMA window
    alpha = 2 / (n + 1)
    
    # 3. Iteratively compute the EMA timeline array
    ema = prices[0]
    for current_price in prices[1:]:
        ema = (current_price * alpha) + (ema * (1 - alpha))
        
    # 4. Extract recent momentum delta to determine trajectory velocity
    recent_window = prices[-5:] if n >= 5 else prices
    recent_change = recent_window[-1] - recent_window[0]
    velocity = recent_change / len(recent_window)
    
    # 5. Project future value out by damping the current velocity trend
    forecasted_price = round(ema + (velocity * days_ahead), 2)
    
    # Ensure a hard floor equal to 30% of the current market value so it never zeroes out
    minimum_allowed_floor = round(prices[-1] * 0.30, 2)
    final_forecast = max(forecasted_price, minimum_allowed_floor)
    
    # Calculate trajectory status description flags
    trajectory = "STABLE"
    if velocity > 0.05:
        trajectory = "UPWARD (Price Hikes Coming)"
    elif velocity < -0.05:
        trajectory = "DOWNWARD (Deals Imminent)"
        
    return {
        "platform": platform_name,
        "historical_data_points": n,
        "smoothing_factor_alpha": round(alpha, 4),
        "current_market_price": prices[-1],
        "calculated_ema_baseline": round(ema, 2),
        "forecasted_days_ahead": days_ahead,
        "predicted_price": final_forecast,
        "market_trajectory": trajectory
    }