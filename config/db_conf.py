import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine,async_sessionmaker

#数据库URL
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
if not ASYNC_DATABASE_URL:
    raise RuntimeError("请在项目根目录的 .env 中配置 ASYNC_DATABASE_URL")

#创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo = True,  #输出SQL日志
    pool_size = 10,       #持久连接数量
    max_overflow = 20,       #额外连接数量
)

#创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

#依赖项
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()