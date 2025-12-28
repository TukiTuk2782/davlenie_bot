import os
from dotenv import load_dotenv

# load_dotenv()
#
# BOT_TOKEN = os.getenv(BOT_TOKEN)
# SPREADSHEET_ID = os.getenv(SPREADSHEET_ID)
# SERVICE_ACCOUNT_FILE = os.getenv(GOOGLE_SERVICE_ACCOUNT_FILE)



BOT_TOKEN = "8504421553:AAFyzGugHGxWdFz4j9x87facB-zX_3sVdwg"
SPREADSHEET_ID = "1bddN_z_xUEsha0kNc1fFaLO8RYTwzCxmoXrMh7Ycms0"
SERVICE_ACCOUNT_FILE = "service_account.json"


if BOT_TOKEN is None:
    print("ОШИБКА: Переменная BOT_TOKEN не загружена из .env!")