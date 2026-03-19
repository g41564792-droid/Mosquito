import os
from datetime import datetime
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
    
    # Получаем список размеров, если есть, иначе используем старые поля
    sizes = data.get('sizes')
    if not sizes:
        # Обратная совместимость: создаем один размер из старых полей
        size_w = data.get('size_w')
        size_h = data.get('size_h')
        qty = data.get('qty', 1)
        if size_w is not None and size_h is not None:
            sizes = [{"width": size_w, "height": size_h, "qty": qty}]
        else:
            sizes = []
    
    if not sizes:
        raise ValueError("Нет данных о размерах для сохранения.")
    
    # Подготавливаем строки для каждого размера
    rows = []
    current_date = datetime.now().strftime("%d.%m.%Y")
    for size in sizes:
        # Объединяем тип установки и подтип через "_"
        install_type = data.get('install_type', '')
        sub_install = data.get('sub_install', '')
        # Убираем возможные невидимые символы
        if install_type:
            install_type = install_type.strip()
        if sub_install:
            sub_install = sub_install.strip()
        if sub_install:
            install_type_full = f"{install_type}_{sub_install}"
        else:
            install_type_full = install_type
        
        # Функция для безопасного получения и очистки строки
        def clean(val):
            if val is None:
                return ''
            if isinstance(val, str):
                return val.strip()
            return str(val).strip()
        
        row = [
            order_id,                                  # A: ID заказа
            current_date,                              # B: Дата заказа
            clean(data.get('client_name')),            # C: Клиент (ID Telegram)
            '',                                        # D: Телефон (пусто)
            install_type_full,                         # E: Тип установки (с подтипом)
            size['width'],                             # F: Ширина
            size['height'],                            # G: Высота
            size.get('qty', 1),                        # H: Кол-во
            clean(data.get('impost', 'no')),           # I: Импост
            clean(data.get('color', 'Не выбран')),     # J: Цвет
            clean(data.get('mount')),                  # K: Крепление
            clean(data.get('fabric', 'Стандартное')),  # L: Полотно
            clean(data.get('notes')),                  # M: Примечание
            '',                                        # N: Цена поз. (пусто)
            '',                                        # O: Сумма (пусто)
            "Новый заказ",                             # P: Статус
            clean(data.get('finish_date'))             # Q: Желаемая дата
        ]
        rows.append(row)
    
    try:
        result = sheet.values().append(
            spreadsheetId=GOOGLE_TABLES_ID,
            range='Zakaz!A:Q',                      # Диапазон столбцов A-Q (17 столбцов)
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': rows}
        ).execute()
        
        print(f"Заказ #{order_id} успешно сохранен. Добавлено {len(rows)} строк.")
        return result
    
    except Exception as e:
        print(f"Ошибка при сохранении заказа: {e}")
        raise