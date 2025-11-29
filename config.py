import os
from dotenv import load_dotenv

load_dotenv()

# If .env doesn't load, use hardcoded values
BOT_TOKEN = os.getenv("BOT_TOKEN") or "8578307013:AAFkFSaxavDiGy1NG2uZlx14aTMVA1WDx-A"
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID") or "-1003215093390"
MAIN_ADMIN_ID = int(os.getenv("MAIN_ADMIN_ID", "6385379310"))

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
