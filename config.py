
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "") # По умолчанию пустая строка при Polling
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# Путь к ключу сервиса Google (можно относительный или абсолютный)
GOOGLE_SERVICE_ACCOUNT_KEY_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY", "./service_account.json")
GOOGLE_TABLES_ID = os.getenv("GOOGLE_TABLES_ID")