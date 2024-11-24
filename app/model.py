from typing import List, Optional

from pydantic import BaseModel


class MessageError(BaseModel):
    message: str
    error: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": f"Message or Error",
                "error": "0"
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str
    access_token_expires: str


class UserToken(BaseModel):
    access_token: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "LOEWJFBweikjBFWowbaowfafoanwAJwfakwjfbwk"
            }
        }


class UserSchema(BaseModel):
    name: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "User007",
                "password": "VeryHardPass"
            }
        }


class CurrentUser(BaseModel):
    id: int
    name: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "2",
                "password": "User007"
            }
        }


class Country(BaseModel):
    country: str


class Genre(BaseModel):
    genre: str


class Film(BaseModel):
    kinopoiskId: int
    kinopoiskHDId: Optional[str] = None
    imdbId: Optional[str] = None
    nameRu: Optional[str] = None
    nameEn: Optional[str] = None
    nameOriginal: Optional[str] = None
    posterUrl: Optional[str] = None
    posterUrlPreview: Optional[str] = None
    coverUrl: Optional[str] = None
    logoUrl: Optional[str] = None
    reviewsCount: Optional[int] = None
    ratingGoodReview: Optional[float] = None
    ratingGoodReviewVoteCount: Optional[int] = None
    ratingKinopoisk: Optional[float] = None
    ratingKinopoiskVoteCount: Optional[int] = None
    ratingImdb: Optional[float] = None
    ratingImdbVoteCount: Optional[int] = None
    ratingFilmCritics: Optional[float] = None
    ratingFilmCriticsVoteCount: Optional[int] = None
    ratingAwait: Optional[float] = None
    ratingAwaitCount: Optional[int] = None
    ratingRfCritics: Optional[float] = None
    ratingRfCriticsVoteCount: Optional[int] = None
    webUrl: Optional[str] = None
    year: Optional[int] = None
    filmLength: Optional[int] = None
    slogan: Optional[str] = None
    description: Optional[str] = None
    shortDescription: Optional[str] = None
    editorAnnotation: Optional[str] = None
    isTicketsAvailable: Optional[bool] = None
    productionStatus: Optional[str] = None
    type: Optional[str] = None
    ratingMpaa: Optional[str] = None
    ratingAgeLimits: Optional[str] = None
    countries: List[Country]
    genres: List[Genre]
    startYear: Optional[int] = None
    endYear: Optional[int] = None
    serial: Optional[bool] = None
    shortFilm: Optional[bool] = None
    completed: Optional[bool] = None
    hasImax: Optional[bool] = None
    has3D: Optional[bool] = None
    lastSync: Optional[str] = None


class FilmSearch(BaseModel):
    filmId: int
    nameRu: Optional[str] = None
    nameEn: Optional[str] = None
    type: Optional[str] = None
    year: Optional[str] = None
    description: Optional[str] = None
    filmLength: Optional[str] = None
    countries: List[Country]
    genres: List[Genre]
    rating: Optional[str] = None
    ratingVoteCount: Optional[int] = None
    posterUrl: Optional[str] = None
    posterUrlPreview: Optional[str] = None


class FilmFavorites(BaseModel):
    id: int
    kinopoisk_id: int
    name: str
