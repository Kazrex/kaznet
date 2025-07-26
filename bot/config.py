import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = "database/ads.db"

# === ОСЫ ЖЕРДЕ ӨЗІҢІЗДІҢ TELEGRAM ID-ІҢІЗ ТҰРУЫ КЕРЕК ===
ADMINS = [6359347300] # Мысал ID