import os

from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.environ["APP_ENV"]
APP_LOG_LEVEL = os.environ["APP_LOG_LEVEL"]

DB_DRIVER = os.environ["DB_DRIVER"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ["DB_PORT"])
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
DB_NAME = os.environ["DB_NAME"]

REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ["REDIS_PORT"])
