from typing import Annotated

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, DeclarativeBase
from sqlalchemy import Column, String, Integer

from app.config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
from app.hash_pass import hash_password


DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL)
SessionFactory = sessionmaker(bind=engine)

Base = declarative_base()


int_pk = Annotated[int, mapped_column(primary_key=True)]
str_256 = Annotated[str, mapped_column(String(256))]


class UsersORM(Base):
    __tablename__ = 'user'
    id: Mapped[int_pk]
    name: Mapped[str_256] = mapped_column(unique=True)
    hash_password: Mapped[str_256] = mapped_column()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

