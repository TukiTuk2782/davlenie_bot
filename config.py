import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
# print(f"SERVICE_ACCOUNT_FILE - {SERVICE_ACCOUNT_FILE}")
GROUP_ID = -1816217507

if BOT_TOKEN is None:
    print("ОШИБКА: Переменная BOT_TOKEN не загружена из .env!")