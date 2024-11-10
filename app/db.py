from typing import Annotated

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, join
from sqlalchemy import String, select, func, and_, desc

from app.config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
from app.hash_pass import hash_password, check_password

DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(url=DATABASE_URL, echo=True)
session_maker = async_sessionmaker(engine)

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


async def async_select_users():
    async with session_maker() as session_sql:
        query = select(UsersORM)
        result_execute = await session_sql.execute(query)
        result = result_execute.scalars().all()
        return result


async def async_is_user_in_table(user_name: str, user_password: str) -> bool:
    async with session_maker() as session_sql:
        query = select(UsersORM).where(UsersORM.name == user_name)
        result_execute = await session_sql.execute(query)
        user = result_execute.scalars().one()
        return check_password(user.hash_password, user_password)


async def async_select_user_by_user_name(user_name: str) -> UsersORM:
    async with session_maker() as session_sql:
        query = select(UsersORM).where(UsersORM.name == user_name)
        result_execute = await session_sql.execute(query)
        user = result_execute.scalars().one()
        return user


# TODO Сделать проверку на то что пользователь уже есть
async def async_insert_user(user_name: str, user_password: str) -> None:
    async with session_maker() as session_sql:
        hashed_user_password = hash_password(user_password)
        user_add = UsersORM(name=user_name, hash_password=hashed_user_password)
        session_sql.add(user_add)
        await session_sql.commit()
