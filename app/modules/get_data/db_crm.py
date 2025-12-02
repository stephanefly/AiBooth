from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = (
    "mysql+aiomysql://stephanefly:mydatabase2778%21"
    "@127.0.0.1:3307/stephanefly$reservation?charset=utf8mb4"
    # <- $ en CLAIR (pas %24)
)

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
