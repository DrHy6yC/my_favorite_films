from os import getenv
from dotenv import load_dotenv

load_dotenv()

DB_HOST: str = getenv('PG_HOST')
DB_PORT: str = getenv('PG_PORT')
DB_USER: str = getenv('PG_USER')
DB_PASS: str = getenv('PG_PASSWORD')
DB_NAME: str = getenv('PG_NAME')

JWT_ALGORITHM: str = getenv('JWT_ALGORITHM')
