from os import getenv
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

load_dotenv()

DB_HOST: str = getenv('PG_HOST')
DB_PORT: str = getenv('PG_PORT')
DB_USER: str = getenv('PG_USER')
DB_PASS: str = getenv('PG_PASSWORD')
DB_NAME: str = getenv('PG_NAME')

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print(DATABASE_URL)

engine = create_async_engine(DATABASE_URL)
SessionFactory = sessionmaker(bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    mobile = relationship("Mobile", uselist=False, backref="owner")

    def __init__(self, name):
        self.name = name


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

