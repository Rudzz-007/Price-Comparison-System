from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

# Updated the port to 5433 to match your active pgAdmin connection exactly!
DATABASE_URL = "postgresql+asyncpg://postgres:Krishna%40770@127.0.0.1:5433/price_aggregator"

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker( #Creates a factory pool that spins up isolated database transaction queries
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db(): #A dependency generator. It hands our API endpoints a safe database connection session when a user makes a request, and automatically closes it when the request finishes
    async with AsyncSessionLocal() as session:
        yield session