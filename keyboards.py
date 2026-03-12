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
    colors = ["Белый", "Коричневый"]
    if install_type == "Проёмный":
        colors.append("Антрацит")
    
    rows = []
    for i in range(0, len(colors), 2):
        row = []
        row.append(InlineKeyboardButton(text=colors[i], callback_data=f"color_{colors[i]}"))
        if i + 1 < len(colors):
            row.append(InlineKeyboardButton(text=colors[i+1], callback_data=f"color_{colors[i+1]}"))
        rows.append(row)
    
    # Добавить RAL только для Проёмный
    if install_type == "Проёмный":
        rows.append([InlineKeyboardButton(text="RAL (свой цвет)", callback_data="color_RAL")])
    
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
            InlineKeyboardButton(text="Антикошка", callback_data="fabric_Antikoška")
        ]
    ])
    return kb

# Дата готовности
def date_kb():
    next_day = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⏱ {next_day} (по умолчанию)", callback_data="date_default")]
    ])
    return kb

# Подтверждение заказа
def confirm_order_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_order"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")
        ]
    ])
    return kb