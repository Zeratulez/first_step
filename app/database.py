from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncAttrs
from app.core.config import settings

engine = create_async_engine(
    url=settings.ASYNC_DATABASE_URL,
    echo=True
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session