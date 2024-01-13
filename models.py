import atexit
import datetime
import os

from sqlalchemy import DateTime, String, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

PG_DSN = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Article(Base):
    __tablename__ = 'app_articles'

    id: Mapped[int] = mapped_column(primary_key=True)
    article: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    date_pub: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    owner: Mapped[str] = mapped_column(String(50), nullable=False)

    @property
    def json(self):
        return {
            'id': self.id,
            'article': self.article,
            'description': self.description,
            'date_pub': self.date_pub,
            'owner': self.owner,
        }


# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

atexit.register(engine.dispose)
