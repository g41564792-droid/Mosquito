from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta

# Главная меню (без использования Builder для простоты)
def main_menu_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛠 Оформить заказ", callback_data="start_order"),
            InlineKeyboardButton(text="❌ Выход", callback_data="cancel_order")
        ]
    ])
    return kb

# Выбор типа установки (Проёмный/Дверной/Роллетный)
def installation_type_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Проёмный", callback_data="type_Proemny"),
            InlineKeyboardButton(text="Дверной", callback_data="type_Dvernoy"),
            InlineKeyboardButton(text="Роллетный", callback_data="type_Rolletny")
        ]
    ])
    return kb

# Подтип проемного (внутренний/наружный)
def proemny_sub_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Наружный", callback_data="sub_Naruzhny"),
            InlineKeyboardButton(text="Внутренний", callback_data="sub_Vnutrenniy"),
            InlineKeyboardButton(text="Встраиваемый", callback_data="sub_Vstraivaemy")
        ]
    ])
    return kb



# Цвет рамы
def color_kb(install_type):
    if install_type == "Проёмный":
        colors = ["Белый", "Коричневый", "Антрацит", "Иной цвет по RAL"]
    else:  # Для дверной и роллетной
        colors = ["Белый", "Коричневый"]

    rows = []
    row = []
    for color in colors:
        row.append(InlineKeyboardButton(text=color, callback_data=f"color_{color}"))
        if len(row) == 2:  # Две кнопки в ряду
            rows.append(row)
            row = []
    
    # Добавляем оставшиеся кнопки в последний ряд
    if row:
        rows.append(row)

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

# Крепление (крепёжные элементы)
def mounting_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Z-кронштейны", callback_data="mount_Z"),
            InlineKeyboardButton(text="Металл зацепы", callback_data="mount_Metal")
        ],
        [
            InlineKeyboardButton(text="Пластик зацепы", callback_data="mount_Plastic"),
            InlineKeyboardButton(text="По умолчанию", callback_data="mount_Default")
        ]
    ])
    return kb

# Импост
def impost_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, добавить импост", callback_data="impost_Yes"),
            InlineKeyboardButton(text="❌ Нет, без импоста", callback_data="impost_No")
        ]
    ])
    return kb

# Ориентация импоста
def orient_impost_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Вертикально", callback_data="orient_Vertical"),
            InlineKeyboardButton(text="Горизонтально", callback_data="orient_Horizontal")
        ]
    ])
    return kb

# Тип полотна (размер сетки)
def fabric_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Стандартное", callback_data="fabric_Standard"),
            InlineKeyboardButton(text="Антипыль", callback_data="fabric_Antipyl")
        ],
        [
            InlineKeyboardButton(text="Антимошка", callback_data="fabric_Antimoska"),
            InlineKeyboardButton(text="Антикошка", callback_data="fabric_Antikoshka")
        ]
    ])
    return kb

import calendar

# Дата готовности
def date_kb(selected_date=None):
    if selected_date is None:
        selected_date = datetime.now() + timedelta(days=1)
    
    # Формируем календарь на текущий месяц
    year = selected_date.year
    month = selected_date.month
    
    # Заголовок месяца
    month_name = selected_date.strftime("%B %Y")
    
    # Создаем клавиатуру
    kb = []
    
    # Навигационные кнопки (переключение месяцев)
    nav_row = [
        InlineKeyboardButton(text="<<", callback_data=f"date_nav_{year}_{month-1}"),
        InlineKeyboardButton(text=month_name, callback_data="date_ignore"),  # Необрабатываемая кнопка
        InlineKeyboardButton(text=">>", callback_data=f"date_nav_{year}_{month+1}")
    ]
    kb.append(nav_row)
    
    # Дни недели
    days_header = [InlineKeyboardButton(text=day, callback_data="date_ignore") for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]]
    kb.append(days_header)
    
    # Получаем первый день месяца и количество дней
    cal = calendar.monthcalendar(year, month)
    
    for week in cal:
        week_row = []
        for day in week:
            if day == 0:  # Пустая ячейка
                week_row.append(InlineKeyboardButton(text=" ", callback_data="date_ignore"))
            else:
                date_obj = datetime(year, month, day)
                date_str = date_obj.strftime("%d.%m.%Y")
                
                # Проверяем, можно ли выбрать эту дату (не раньше чем завтра)
                tomorrow = datetime.now() + timedelta(days=1)
                if date_obj.date() >= tomorrow.date():
                    week_row.append(InlineKeyboardButton(text=str(day), callback_data=f"date_select_{date_str}"))
                else:
                    week_row.append(InlineKeyboardButton(text="•", callback_data="date_ignore"))
        
        kb.append(week_row)
    
    # Кнопка "По умолчанию" (завтра)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
    kb.append([InlineKeyboardButton(text=f"⏱ {tomorrow} (по умолчанию)", callback_data=f"date_select_{tomorrow}")])
    
    # Кнопка ручного ввода
    kb.append([InlineKeyboardButton(text="📝 Ввести дату вручную", callback_data="date_manual")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

# Подтверждение заказа
def confirm_order_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_order"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")
        ]
    ])
    return kb