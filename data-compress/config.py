import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("user")
password = os.getenv("password")
database_name = os.getenv("database_name")


class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{username}:{password}@localhost:5432/{database_name}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
