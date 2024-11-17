import aiohttp
import asyncio
from fastapi import FastAPI, Depends

from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import sign_jwt, decode_jwt
from app.db import create_tables, async_insert_user, async_is_user_in_table, async_select_user_by_user_name
from app.config import HEADERS, KINOPOISK_URL, SEARCH_BY_KEYWORD, GET_FILM_BY_ID
from app.model import UserSchema


app = FastAPI()


# route handlers
@app.get("/create_all_tables", tags=["create_all_tables"])
async def create_all_tables() -> dict:
    await create_tables()
    return {"message": "All tables have been created"}


@app.post("/register", tags=["user"])
async def create_user(user: UserSchema):
    await async_insert_user(user.name, user.password)
    return {"message": f"{user.name} have been created"}


@app.post("/login", tags=["user"])
async def user_login(user: UserSchema):
    if await async_is_user_in_table(user.name, user.password):
        return sign_jwt(user.name)
    return {
        "error": "Wrong login details!"
    }


@app.get("/profile", tags=["user"], dependencies=[Depends(JWTBearer())])
async def get_current_user(token=Depends(JWTBearer())):
    current_user_name: str = decode_jwt(token)['user_name']
    current_user_db: UserSchema = await async_select_user_by_user_name(current_user_name)
    # TODO Убрать пароль из отображения
    return current_user_db


@app.get("/movies/search", tags=["films"], dependencies=[Depends(JWTBearer())])
async def get_film_on_name(query: str):

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(f"{KINOPOISK_URL}/{SEARCH_BY_KEYWORD}={query}") as r:
            json_body = await r.json()
    return json_body


@app.get("/movies/{kinopoisk_id}", tags=["films"], dependencies=[Depends(JWTBearer())])
async def get_film_on_id(kinopoisk_id: int):

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(f"{KINOPOISK_URL}/{GET_FILM_BY_ID}/{kinopoisk_id}") as r:
            json_body = await r.json()
    return json_body
