import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

SECRET_KEY = os.urandom(32)

SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(
    DB_USER,
    DB_PASSWORD,
    'localhost:5432',
    DB_NAME
)

SQLALCHEMY_TRACK_MODIFICATIONS = False