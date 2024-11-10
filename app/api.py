from fastapi import FastAPI, Body, Depends

from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import sign_jwt
from app.model import PostSchema, UserSchema
from app.db import create_tables
from app.hash_pass import check_password


posts = [
    {
        "id": 1,
        "title": "Pancake",
        "content": "Lorem Ipsum ..."
    }
]

users = []

app = FastAPI()


def check_user(data: UserSchema):
    for user in users:
        if user.name == data.name and user.password == data.password:
            return True
    return False


# route handlers
@app.get("/create_all_tables", tags=["create_all_tables"])
async def create_all_tables() -> dict:
    await create_tables()
    return {"message": "All tables have been created"}


@app.post("/register", tags=["user"])
async def create_user(user: UserSchema = Body(...)):
    users.append(user)
    return {"message": f"{user.name} have been created"}


@app.post("/login", tags=["user"])
async def user_login(user: UserSchema = Body(...)):
    if check_user(user):
        return sign_jwt(user.name)
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
