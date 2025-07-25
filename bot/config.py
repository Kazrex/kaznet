import os
from dotenv import load_dotenv

# .env файлынан айнымалыларды жүктеу
load_dotenv()

# Telegram бот токені
# .env файлындағы BOT_TOKEN айнымалысынан оқылады
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Дерекқор файлының жолы
DB_PATH = "database/ads.db"

# Әкімшілердің ID тізімі (қажет болса)
ADMINS = [6359347300] # Мысал ID, өзіңіздікін қойыңыз