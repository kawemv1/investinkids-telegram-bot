ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID") or "-1003215093390"
MAIN_ADMIN_ID = int(os.getenv("MAIN_ADMIN_ID", "6385379310"))

DB_HOST = os.getenv("DB_HOST") or "192.168.8.130"
DB_PORT = os.getenv("DB_PORT") or "5434"
DB_NAME = os.getenv("DB_NAME") or "n8n"
DB_USER = os.getenv("DB_USER") or "n8n_user"
DB_PASSWORD = os.getenv("DB_PASSWORD") or "StrongPass_Invest2025"
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

