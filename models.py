import datetime
import os

from dotenv import load_dotenv
from sqlalchemy import DateTime, String, func
from sqlalchemy.ext.asyncio import (AsyncAttrs, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

PG_DSN = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Article(Base):
    __tablename__ = "app_articles_aiohttp"

    id: Mapped[int] = mapped_column(primary_key=True)
    article: Mapped[str] = mapped_column(
        String(150), unique=True, index=True, nullable=False
    )
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    date_pub: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    owner: Mapped[str] = mapped_column(String(50), nullable=False)

    @property
    def json(self):
        return {
            "id": self.id,
            "article": self.article,
            "description": self.description,
            "date_pub": int(self.date_pub.timestamp()),
            "owner": self.owner,
        }


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
