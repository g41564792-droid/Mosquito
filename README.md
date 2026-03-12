# Mosquitonet Bot

Telegram-бот для заказа москитных сеток. Позволяет пользователям оформлять заказы на москитные сетки через удобное интерфейсное взаимодействие с ботом.

## Функциональность

- Оформление заказа на москитные сетки
- Выбор типа установки (Проёмный, Дверной, Роллетный)
- Настройка размеров изделия
- Выбор цвета рамы и типа полотна
- Сохранение заказов в Google Таблицы

## Требования

- Python 3.8+
- Aiogram 3.x
- Google API Client Library

## Установка

1. Установите зависимости:
   ```bash
   pip install aiogram python-dotenv google-auth google-api-python-client
   ```

2. Создайте файл `.env` с необходимыми переменными:
   ```
   TG_BOT_TOKEN=your_telegram_bot_token
   ADMIN_CHAT_ID=your_admin_chat_id
   GOOGLE_SERVICE_ACCOUNT_KEY=./service_account.json
   GOOGLE_TABLES_ID=your_google_spreadsheet_id
   ```

3. Настройте Google Service Account и добавьте файл `service_account.json`

## Использование

Запустите бота командой:
```bash
python main.py
```

## Структура проекта

- `main.py` - основной файл запуска бота
- `handler_order.py` - обработчики заказов и FSM состояния
- `keyboards.py` - inline клавиатуры для взаимодействия
- `config.py` - конфигурация и переменные окружения
- `google_sheets.py` - интеграция с Google Таблицами
- `utils.py` - вспомогательные функции