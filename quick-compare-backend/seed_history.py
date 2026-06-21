import asyncio
import random
from datetime import datetime, timedelta, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models import ProductPriceHistory

ITEMS = {
    "maggi": {"base": 14.0, "qty": "1 Pack"},
    "milk": {"base": 33.0, "qty": "500 ml"},
    "bread": {"base": 45.0, "qty": "400g"}
}

PLATFORMS = ["Blinkit", "Zepto", "Swiggy Instamart"]

async def seed_data():
    print("[SEEDER] Connecting to PostgreSQL to populate 30-day analytical matrix...")
    async with AsyncSessionLocal() as db:
        for day in range(30, 0, -1):
            # The line has been fully replaced below to prevent the deprecation warning
            target_date = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=day)
            
            for item_name, details in ITEMS.items():
                for platform in PLATFORMS:
                    market_variance = random.uniform(-3.5, 4.0)
                    historical_price = round(max(details["base"] + market_variance, 5.0), 2)
                    
                    history_entry = ProductPriceHistory(
                        query_term=item_name,
                        platform=platform,
                        title=f"{item_name.capitalize()} Value Pack",
                        price=historical_price,
                        quantity=details["qty"],
                        timestamp=target_date
                    )
                    db.add(history_entry)
                    
        await db.commit()
    print("[SEEDER SUCCESS] 270 historical pricing indexes successfully injected into PostgreSQL!")

if __name__ == "__main__":
    asyncio.run(seed_data())