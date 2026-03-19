import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import GOOGLE_SERVICE_ACCOUNT_KEY_PATH, GOOGLE_TABLES_ID, GOOGLE_SCOPES


def get_spreadsheet():
    if not os.path.exists(GOOGLE_SERVICE_ACCOUNT_KEY_PATH):
        raise FileNotFoundError(f"Ключевой файл Google Sheets не найден по пути: {GOOGLE_SERVICE_ACCOUNT_KEY_PATH}")

    try:
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_SERVICE_ACCOUNT_KEY_PATH, scopes=GOOGLE_SCOPES
        )
        
        # Проверка токена, если истек, он перезапишется автоматически при следующем запросе
        if credentials.expired:
            credentials.refresh()
            
        service = build('sheets', 'v4', credentials=credentials)
        return service.spreadsheets()
    
    except Exception as e:
        raise ConnectionError(f"Ошибка авторизации в Google Sheets: {e}")

def save_order_to_sheet(order_id, data):
    """
    Сохраняет заявку клиента в Google Таблицу.
    order_id: Уникальный идентификатор заказа (строка)
    data: Словарь с данными заказа (размер, цвет, имя и т.д.)
    """
    sheet = get_spreadsheet()
    
    # Формируем значения для нового листа (OrderLog) или конкретного диапазона
    values = [
        [
            order_id,                          # A: ID заказа
            data.get('install_type'),          # B: Тип установки
            data.get('sub_install', ''),       # C: Подтип
            f"{data['size_w']}x{data['size_h']}", # D: Размер
            data.get('qty', 1),                # E: Количество
            data.get('color', 'Не выбран'),    # F: Цвет
            data.get('fabric', 'Стандартное'), # G: Полотно
            data.get('impost', 'no'),          # H: Импост
            data.get('notes', ''),             # I: Примечание
            "Новый заказ",                     # J: Статус
            data.get('client_name', '')        # K: Клиент
        ]
    ]
    
    try:
        result = sheet.values().append(
            spreadsheetId=GOOGLE_TABLES_ID,
            range='Лист1',                      # Или другой лист, например 'Заказы'
            valueInputOption='RAW',
            body={'values': values}
        ).execute()
        
        print(f"Заказ #{order_id} успешно сохранен.")
        return result
    
    except Exception as e:
        print(f"Ошибка при сохранении заказа: {e}")
        raise