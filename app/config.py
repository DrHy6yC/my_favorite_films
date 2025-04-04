from os import getenv
from dotenv import load_dotenv

load_dotenv()

DB_HOST: str = getenv('PG_HOST')
DB_PORT: str = getenv('PG_PORT')
DB_USER: str = getenv('PG_USER')
DB_PASS: str = getenv('PG_PASSWORD')
DB_NAME: str = getenv('PG_NAME')

JWT_ALGORITHM: str = getenv('JWT_ALGORITHM')
JWT_SECRET: str = getenv('JWT_SECRET')
TOKEN_LIFETIME: str = getenv('TOKEN_LIFETIME')

KINOPOISK_API: str = getenv('KINOPOISK_API')

HEADERS = {
        "Content-Type": "application/json",
        "X-API-KEY": KINOPOISK_API
    }

KINOPOISK_URL: str = 'https://kinopoiskapiunofficial.tech'
SEARCH_BY_KEYWORD: str = 'api/v2.1/films/search-by-keyword?keyword'
FILMS: str = 'api/v2.2/films'
