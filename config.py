import os
from pathlib import Path
from dotenv import load_dotenv

# Этот метод работает ВЕЗДЕ. Он берет путь к папке, где лежит САМ config.py
# На сервере это будет, например, /var/www/bot, и код это поймет автоматически.
BASE_DIR = Path(__file__).resolve().parent

# Загружаем .env, который лежит в той же папке, что и этот скрипт
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Теперь достаем переменные
BOT_TOKEN = os.getenv("BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json")

GROUP_ID = -1003574487578

# Проверка для тебя (в консоли сервера увидишь, если что-то не так)
if not BOT_TOKEN:
    print(f"❌ ОШИБКА: .env не найден или пуст в директории {BASE_DIR}")
else:
    print(f"✅ Бот успешно прочитал настройки из {BASE_DIR}")
