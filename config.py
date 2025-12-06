import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# If .env doesn't load, use hardcoded values
BOT_TOKEN = os.getenv("BOT_TOKEN") or "8578307013:AAFkFSaxavDiGy1NG2uZlx14aTMVA1WDx-A"
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID") or "-1003215093390"
MAIN_ADMIN_ID = int(os.getenv("MAIN_ADMIN_ID", "6385379310"))
# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID")
MAIN_ADMIN_ID = int(os.getenv("MAIN_ADMIN_ID", "0"))

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
# PostgreSQL Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "investinkids")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Build PostgreSQL connection string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Validate required configuration
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is required! Please set it in .env file")
if not ADMIN_GROUP_ID:
    raise ValueError("ADMIN_GROUP_ID is required! Please set it in .env file")
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD is required! Please set it in .env file")
