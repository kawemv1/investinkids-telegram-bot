import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID")
MAIN_ADMIN_ID = int(os.getenv("MAIN_ADMIN_ID", "0"))

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
