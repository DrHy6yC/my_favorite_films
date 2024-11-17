import aiohttp

from fastapi import FastAPI, Depends

from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import sign_jwt, decode_jwt
from app.db import async_insert_film, async_insert_favorites, create_tables, async_insert_user, async_is_user_in_table, async_select_user_by_user_name
from app.config import HEADERS, KINOPOISK_URL, SEARCH_BY_KEYWORD, FILMS
from app.model import UserSchema, CurrentUser, UserToken, Film, FilmSearch, MessageError


app = FastAPI()


@app.get("/create_all_tables", tags=["create_all_tables"])
async def create_all_tables() -> dict:
    await create_tables()
    return {
        "message": "All tables have been created",
        "error": "0"
    }


@app.post("/register", tags=["user"])
async def create_user(user: UserSchema) -> UserToken:
    await async_insert_user(user.name, user.password)
    token = sign_jwt(user.name)
    return token


@app.post("/login", tags=["user"])
async def user_login(user: UserSchema) -> UserToken:
    if await async_is_user_in_table(user.name, user.password):
        token = sign_jwt(user.name)
    else:
        token = {
                "access_token": "Wrong login details!"
            }
    return token


@app.get("/profile", tags=["user"], dependencies=[Depends(JWTBearer())])
async def get_current_user(token=Depends(JWTBearer())) -> CurrentUser:
    current_user_name: str = decode_jwt(token)['user_name']
    current_user_db: CurrentUser = await async_select_user_by_user_name(current_user_name)
    return current_user_db


@app.get("/movies/search", tags=["films"], dependencies=[Depends(JWTBearer())])
async def get_film_on_name(query: str):
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


#TODO Сделать проверку если фильм уже есть в избранном
@app.post("/movies/favorites/{kinopoisk_id}", tags=["films"], dependencies=[Depends(JWTBearer())])
async def add_film_to_favorites(kinopoisk_id: int, token=Depends(JWTBearer())) -> MessageError:
    user: CurrentUser = await get_current_user(token)
    film: Film = await get_film_on_id(kinopoisk_id)
    try:
        await async_insert_film(film['kinopoiskId'], film['nameRu'])
    except:
        pass
    await async_insert_favorites(film['kinopoiskId'], user.id)
    return {
        "message": f"Film with id = {kinopoisk_id} is added  to {user.name}'s favorites",
        "error": "0"
    }


@app.delete("/movies/favorites/{kinopoisk_id}", tags=["films"], dependencies=[Depends(JWTBearer())])
async def delete_film_to_favorites(kinopoisk_id: int, token=Depends(JWTBearer())) -> MessageError:
    user: CurrentUser = await get_current_user(token)

    return {
        "message": f"Film with id = {kinopoisk_id} is added  to {user.name}'s favorites",
        "error": "0"
    }