from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str
    access_token_expires: str


class UserSchema(BaseModel):
    name: str = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "User007",
                "password": "VeryHardPass"
            }
        }


class CurrentUser(BaseModel):
    id: int = Field(...)
    name: str = Field(...)


