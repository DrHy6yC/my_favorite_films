import aiohttp

from fastapi import FastAPI, Depends, status, Response

from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import sign_jwt, decode_jwt
from app.db import async_insert_film, async_insert_favorites, create_tables, async_insert_user,\
    async_is_user_in_table, async_select_user_by_user_name, async_delete_favorites
from app.config import HEADERS, KINOPOISK_URL, SEARCH_BY_KEYWORD, FILMS
from app.model import UserSchema, CurrentUser, UserToken, Film, FilmSearch, MessageError

app = FastAPI()


#TODO добавить статус коды, обработка ошибок
@app.get(
    "/create_all_tables",
    tags=["create_all_tables"],
    responses={
        201: {"model": MessageError},
        500: {"model": MessageError}
    }
)
async def create_all_tables(response: Response) -> MessageError:
    try:
        await create_tables()
        status_code = status.HTTP_201_CREATED
        message = "All tables have been created"
        error = "0"
    except OSError as oserr:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        print(oserr)
        message = "DB Error"
        error = "-1"
    except Exception as err:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        print(err)
        message = "Server Error"
        error = "-2"
    response.status_code = status_code
    result = MessageError(
        message=message,
        error=error
    )
    return result


@app.post(
    "/register",
    tags=["user"],
    responses={
        201: {"model": UserToken}
    }
)
#TODO Дописать статус коды когда БД не доступна, когда неправильный запрос
async def create_user(response: Response, user: UserSchema) -> UserToken|MessageError:
    await async_insert_user(user.name, user.password)
    token = sign_jwt(user.name)
    status_code = status.HTTP_201_CREATED
    response.status_code = status_code
    return token


@app.post(
    "/login",
    tags=["user"],
    responses={
        200: {"model": UserToken},
        401: {"model": UserToken}
    }
)
async def user_login(response: Response, user: UserSchema) -> UserToken:
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


@app.get("/profile", tags=["user"], dependencies=[Depends(JWTBearer())])
async def get_current_user(token=Depends(JWTBearer())) -> CurrentUser:
    current_user_name: str = decode_jwt(token)['user_name']
    current_user_db: CurrentUser = await async_select_user_by_user_name(current_user_name)
    return current_user_db


@app.get("/movies/search", tags=["films"], dependencies=[Depends(JWTBearer())])
async def get_film_on_name(query: str) -> list[FilmSearch]:
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(f"{KINOPOISK_URL}/{SEARCH_BY_KEYWORD}={query}") as r:
            json_body = await r.json()
            films = json_body["films"]
    return films


@app.get("/movies/{kinopoisk_id}", tags=["films"], dependencies=[Depends(JWTBearer())])
async def get_film_on_id(kinopoisk_id: int) -> Film:
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(f"{KINOPOISK_URL}/{FILMS}/{kinopoisk_id}") as r:
            json_body = await r.json()
    return json_body


# TODO Сделать проверку если фильм уже есть в избранном
@app.post("/movies/favorites/{kinopoisk_id}", tags=["films"], dependencies=[Depends(JWTBearer())])
async def add_film_to_favorites(kinopoisk_id: int, token=Depends(JWTBearer())) -> MessageError:
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


@app.delete("/movies/favorites/{kinopoisk_id}", tags=["films"], dependencies=[Depends(JWTBearer())])
async def delete_film_from_favorites(kinopoisk_id: int, token=Depends(JWTBearer())) -> MessageError:
    user: CurrentUser = await get_current_user(token)
    await async_delete_favorites(kinopoisk_id, user.id)
    result = MessageError(
        message=f"Film with id = {kinopoisk_id} is deleted to {user.name}'s favorites",
        error="0"
    )
    return result
