from fastapi import FastAPI, Body, Depends

from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import sign_jwt
from app.model import PostSchema, UserSchema, UserLoginSchema
from app.db import create_tables


posts = [
    {
        "id": 1,
        "title": "Pancake",
        "content": "Lorem Ipsum ..."
    }
]

users = []

app = FastAPI()


def check_user(data: UserLoginSchema):
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False


# route handlers
@app.get("/create_all_tables", dependencies=[Depends(JWTBearer())], tags=["create_all_tables"])
async def create_all_tables() -> dict:
    await create_tables()
    return {"message": "All tables have been created"}


@app.post("/user/signup", tags=["user"])
async def create_user(user: UserSchema = Body(...)):
    users.append(user)
    return sign_jwt(user.email)


@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return sign_jwt(user.email)
    return {
        "error": "Wrong login details!"
    }


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
