from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import ProductPriceHistory

async def get_price_trends(query_term: str, db: AsyncSession):
    """
    Calculates advanced analytical insights from historical data records 
    to provide metrics for our pricing engine.
    """
    # 1. Fetch the overall average, lowest, and highest prices ever recorded for this term
    summary_query = select(
        func.avg(ProductPriceHistory.price).label("avg_price"),
        func.min(ProductPriceHistory.price).label("min_price"),
        func.max(ProductPriceHistory.price).label("max_price"),
        func.count(ProductPriceHistory.id).label("total_records")
    ).where(ProductPriceHistory.query_term.ilike(f"%{query_term}%"))
    
    summary_result = await db.execute(summary_query)
    summary = summary_result.mappings().first()
    
    # 2. Group insights by platform to see who has the best historical deals
    platform_query = select(
        ProductPriceHistory.platform,
        func.avg(ProductPriceHistory.price).label("platform_avg"),
        func.min(ProductPriceHistory.price).label("platform_min"),
        # Standard deviation calculates price volatility over time
        func.stddev(ProductPriceHistory.price).label("price_volatility")
    ).where(
        ProductPriceHistory.query_term.ilike(f"%{query_term}%")
    ).group_by(
        ProductPriceHistory.platform
    )
    
    platform_result = await db.execute(platform_query)
    platform_trends = platform_result.mappings().all()
    
    # Format the data cleanly into a structure our API can serve
    return {
        "item": query_term,
        "market_summary": {
            "average_market_price": round(summary["avg_price"] or 0.0, 2),
            "lowest_historical_price": round(summary["min_price"] or 0.0, 2),
            "highest_historical_price": round(summary["max_price"] or 0.0, 2),
            "total_datapoints_collected": summary["total_records"]
        },
        "platform_breakdown": [
            {
                "platform": row["platform"],
                "historical_average": round(row["platform_avg"] or 0.0, 2),
                "historical_lowest": round(row["platform_min"] or 0.0, 2),
                "volatility_index": round(row["price_volatility"] or 0.0, 2)
            } for row in platform_trends
        ]
    }