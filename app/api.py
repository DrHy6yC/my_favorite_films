from fastapi import FastAPI, Body, Depends

from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import sign_jwt, decode_jwt
from app.model import PostSchema, UserSchema, CurrentUser
from app.db import create_tables, async_insert_user, async_is_user_in_table, async_select_user_by_user_name, UsersORM

posts = [
    {
        "id": 1,
        "title": "Pancake",
        "content": "Lorem Ipsum ..."
    }
]

app = FastAPI()


# route handlers
@app.get("/create_all_tables", tags=["create_all_tables"])
async def create_all_tables() -> dict:
    await create_tables()
    return {"message": "All tables have been created"}


@app.post("/register", tags=["user"])
async def create_user(user: UserSchema = Body(...)):
    await async_insert_user(user.name, user.password)
    return {"message": f"{user.name} have been created"}


@app.post("/login", tags=["user"])
async def user_login(user: UserSchema = Body(...)):
    if await async_is_user_in_table(user.name, user.password):
        return sign_jwt(user.name)
    return {
        "error": "Wrong login details!"
    }


@app.get("/profile", tags=["user"], dependencies=[Depends(JWTBearer())])
async def get_current_user(token=Depends(JWTBearer())):
    current_user_name: str = decode_jwt(token)['user_name']
    current_user_db = await async_select_user_by_user_name(current_user_name)
    # TODO Убрать пароль из отображения
    return current_user_db


@app.get("/posts", tags=["posts"])
async def get_posts() -> dict:
    return {"data": posts}


@app.get("/posts/{id}", tags=["posts"])
async def get_single_post(id_post: int) -> dict:
    if id_post > len(posts):
        return {
            "error": "No such post with the supplied ID."
        }

    for post in posts:
        if post["id"] == id_post:
            return {
                "data": post
            }


@app.post("/posts", dependencies=[Depends(JWTBearer())], tags=["posts"])
async def add_post(post: PostSchema) -> dict:
    post.id = len(posts) + 1
    posts.append(post.dict())
    return {
        "data": "post added."
    }
