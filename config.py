import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TG_BOT_TOKEN не задан в .env")

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "") # По умолчанию пустая строка при Polling

ADMIN_CHAT_ID_STR = os.getenv("ADMIN_CHAT_ID")
if ADMIN_CHAT_ID_STR is None:
    raise ValueError("ADMIN_CHAT_ID не задан в .env")
try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID_STR)
except ValueError:
    raise ValueError("ADMIN_CHAT_ID должен быть целым числом")

# Путь к ключу сервиса Google (можно относительный или абсолютный)
GOOGLE_SERVICE_ACCOUNT_KEY_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY", "./service_account.json")
GOOGLE_TABLES_ID = os.getenv("GOOGLE_TABLES_ID")
if not GOOGLE_TABLES_ID:
    raise ValueError("GOOGLE_TABLES_ID не задан в .env")

GOOGLE_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']