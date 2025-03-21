import aiohttp

from fastapi import FastAPI, Depends, status, Response, HTTPException

from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import sign_jwt, decode_jwt
from app.db import async_insert_film, async_insert_favorites, create_tables, async_insert_user, \
    async_is_user_in_table, async_select_user_by_user_name, async_delete_favorites, \
    async_select_favorites_current_user
from app.config import HEADERS, KINOPOISK_URL, SEARCH_BY_KEYWORD, FILMS
from app.model import UserSchema, CurrentUser, UserToken, Film, FilmSearch, MessageError, FilmFavorites

app = FastAPI()


@app.get(
    path="/",
    tags=["Greeting"],
    responses={
        200: {"model": MessageError}
    }
)
async def api_greeting() -> MessageError:
    result = MessageError(
        message="Приветствуем на апи по поиску фильмов в кинопоиске!",
        error="0"
    )
    return result


# TODO добавить статус коды, обработка ошибок
@app.get(
    path="/create_all_tables",
    tags=["Create all tables"],
    responses={
        201: {"model": MessageError},
        500: {"model": MessageError}
    }
)
async def create_all_tables(
        response: Response
) -> MessageError:
    try:
        await create_tables()
        status_code = status.HTTP_201_CREATED
        message = "All tables have been created"
        error = "0"
    except OSError as oserror:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        print(oserror)
        message = "DB Error"
        error = "-1"
    except Exception as error:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        print(error)
        message = "Server Error"
        error = "-2"
    response.status_code = status_code
    result = MessageError(
        message=message,
        error=error
    )
    return result


@app.post(
    path="/register",
    tags=["user"],
    responses={
        201: {"model": UserToken},
        500: {"model": MessageError}
    }
)
# TODO Дописать статус коды когда БД не доступна, когда неправильный запрос
async def create_user(
        response: Response,
        user: UserSchema
) -> UserToken | MessageError:
    try:
        await async_insert_user(user.name, user.password)
        token = sign_jwt(user.name)
        response.status_code = status.HTTP_201_CREATED
        return token
    except Exception as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        print(error)
        return MessageError(
            message="error",
            error="1"
        )


@app.post(
    path="/login",
    tags=["user"],
    responses={
        200: {"model": UserToken},
        401: {"model": UserToken}
    }
)
async def user_login(
        response: Response,
        user: UserSchema
) -> UserToken:
    if await async_is_user_in_table(user.name, user.password):
        token = sign_jwt(user.name)
        status_code = status.HTTP_200_OK
    else:
        # TODO сделать ошибку авторизации со статус кодом
        token = UserToken(
            access_token="Wrong login details!"
        )
        status_code = status.HTTP_401_UNAUTHORIZED
    response.status_code = status_code
    return token


@app.get(
    path="/profile",
    tags=["user"],
    dependencies=[Depends(JWTBearer())]
)
async def get_current_user(
        token=Depends(JWTBearer())
) -> CurrentUser:
    current_user_name: str = decode_jwt(token)['user_name']
    current_user_db: CurrentUser = await async_select_user_by_user_name(current_user_name)
    return current_user_db


@app.get(
    path="/movies/search",
    tags=["films"],
    dependencies=[Depends(JWTBearer())]
)
async def get_film_on_name(
        query: str
) -> list[FilmSearch]:
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(f"{KINOPOISK_URL}/{SEARCH_BY_KEYWORD}={query}", ssl=False) as r:
            json_body = await r.json()
            films = json_body["films"]
    return films


@app.get(
    path="/movies/{kinopoisk_id}",
    tags=["films"],
    dependencies=[Depends(JWTBearer())]
)
async def get_film_on_id(
        kinopoisk_id: int
) -> Film:
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(f"{KINOPOISK_URL}/{FILMS}/{kinopoisk_id}", ssl=False) as r:
            json_body = await r.json()
    return json_body


# TODO Сделать проверку если фильм уже есть в избранном
@app.post(
    path="/movies/favorites/{kinopoisk_id}",
    tags=["films"],
    dependencies=[Depends(JWTBearer())]
)
async def add_film_to_favorites(
        kinopoisk_id: int,
        token=Depends(JWTBearer())
) -> MessageError:
    user: CurrentUser = await get_current_user(token)
    film: Film = await get_film_on_id(kinopoisk_id)
    try:
        await async_insert_film(film['kinopoiskId'], film['nameRu'])
    finally:
        await async_insert_favorites(film['kinopoiskId'], user.id)
        result = MessageError(
            message=f"Film with id = {kinopoisk_id} is added  to {user.name}'s favorites",
            error="0"
        )
    return result


@app.delete(
    path="/movies/favorites/{kinopoisk_id}",
    tags=["films"],
    dependencies=[Depends(JWTBearer())]
)
async def delete_film_from_favorites(
        kinopoisk_id: int,
        token=Depends(JWTBearer())
) -> MessageError:
    user: CurrentUser = await get_current_user(token)
    await async_delete_favorites(kinopoisk_id, user.id)
    result = MessageError(
        message=f"Film with id = {kinopoisk_id} is deleted to {user.name}'s favorites",
        error="0"
    )
    return result


@app.get(
    path="/movies/favorites/",
    tags=["films"],
    dependencies=[Depends(JWTBearer())]
)
async def get_favorites_films_current_user(
        token=Depends(JWTBearer())
) -> list[FilmFavorites]:
    user: CurrentUser = await get_current_user(token)
    result = await async_select_favorites_current_user(user.id)
    return result
