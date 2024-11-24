from typing import Annotated

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, select, ForeignKey

from app.config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
from app.hash_pass import hash_password, check_password

DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(url=DATABASE_URL, echo=True)
session_maker = async_sessionmaker(engine)

Base = declarative_base()

int_pk = Annotated[int, mapped_column(primary_key=True)]
str_256 = Annotated[str, mapped_column(String(256))]


class UserORM(Base):
    __tablename__ = 'user'
    id: Mapped[int_pk]
    name: Mapped[str_256] = mapped_column(unique=True)
    hash_password: Mapped[str_256]


class FilmORM(Base):
    __tablename__ = 'film'
    id: Mapped[int_pk]
    kinopoisk_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str_256]


class FavoriteORM(Base):
    __tablename__ = 'favorite'
    id: Mapped[int_pk]
    id_user: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'))
    id_kinopoisk: Mapped[int] = mapped_column(ForeignKey('film.kinopoisk_id', ondelete='CASCADE', onupdate='CASCADE'))


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def async_is_user_in_table(user_name: str, user_password: str) -> bool:
    async with session_maker() as session_sql:
        try:
            query = select(UserORM).where(UserORM.name == user_name)
            result_execute = await session_sql.execute(query)
            user = result_execute.scalars().one()
            return check_password(user.hash_password, user_password)
        except Exception as error:
            print(error)
            return False


async def async_select_user_by_user_name(user_name: str) -> UserORM:
    async with session_maker() as session_sql:
        query = select(UserORM).where(UserORM.name == user_name)
        result_execute = await session_sql.execute(query)
        user = result_execute.scalars().one()
        return user


# TODO Сделать проверку на то что пользователь уже есть
async def async_insert_user(user_name: str, user_password: str) -> None:
    async with session_maker() as session_sql:
        hashed_user_password = hash_password(user_password)
        user_add = UserORM(name=user_name, hash_password=hashed_user_password)
        session_sql.add(user_add)
        await session_sql.commit()


#TODO проверка того что уже есть фильм с таким же kinopoisk_id
async def async_insert_film(film_id: int, film_name: str) -> None:
    async with session_maker() as session_sql:
        film_add = FilmORM(kinopoisk_id=film_id, name=film_name)
        session_sql.add(film_add)
        await session_sql.commit()


async def async_insert_favorites(kinopoisk_id: int, user_id: int) -> None:
    async with session_maker() as session_sql:
        favorite_add = FavoriteORM(id_kinopoisk=kinopoisk_id, id_user=user_id)
        session_sql.add(favorite_add)
        await session_sql.commit()


#TODO проверка того что фильм с таким kinopoisk_id существует
async def async_delete_favorites(kinopoisk_id: int, user_id: int) -> None:
    async with session_maker() as session_sql:
        async with session_sql.begin():
            result = await session_sql.execute(
                select(FavoriteORM).
                where(FavoriteORM.id_kinopoisk == kinopoisk_id, FavoriteORM.id_user == user_id)
            )
            favorite = result.scalars().first()
            await session_sql.delete(favorite)
            await session_sql.commit()


async def async_select_favorites_current_user(user_id: int) -> list[FilmORM]:
    async with session_maker() as session_sql:
        query = select(FilmORM).join(FavoriteORM).where(FavoriteORM.id_user == user_id)
        result_execute = await session_sql.execute(query)
        films = result_execute.scalars().all()
        return films
