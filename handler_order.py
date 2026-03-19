import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from datetime import datetime, timedelta
from keyboards import main_menu_kb  # Импортируем готовую функцию


router = Router()

class OrderForm(StatesGroup):
    name = State()
    phone = State()
    install_type = State()
    sub_install = State()
    size_w = State()
    size_h = State()
    qty = State()
    color = State()
    color_description = State()
    mount = State()
    fabric = State()
    impost = State()
    orient = State()
    finish_date = State()
    notes = State()
    summary = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    # Используем нашу новую тестовую функцию
    await message.answer("Здравствуйте! Это бот для заказа москитной сетки.", reply_markup=main_menu_kb())

# Исправленный callback_начало
@router.callback_query(F.data == "start_order")
async def start_order(call: CallbackQuery, state: FSMContext):
    # Импортируем здесь, чтобы избежать циклических зависимостей
    from keyboards import installation_type_kb 
    if call.message:
        await call.message.answer("Начнем оформление нового заказа. 🛠", reply_markup=installation_type_kb())
    await state.set_state(OrderForm.install_type)

@router.callback_query(F.data.startswith("type_"))
async def set_install_type(call: CallbackQuery, state: FSMContext):
    from keyboards import proemny_sub_kb
    
    if call.data:
        install_type_code = call.data.split("_")[1]  # Proemny, Dvernoy, Rolletny
    else:
        install_type_code = ""
    
    # Преобразуем код типа в русское название
    type_map = {
        "Proemny": "Проёмный",
        "Dvernoy": "Дверной",
        "Rolletny": "Роллетный"
    }
    install_type = type_map.get(install_type_code, install_type_code)
    
    # Обновляем данные состояния
    await state.update_data({"install_type": install_type})
    
    if install_type == "Проёмный":
        # Отправляем ОДНО сообщение с текстом и кнопками одновременно!
        if call.message:
            await call.message.answer(
                "*Проёмный тип установки*\n\n📍 Выберите подтип монтажа:",
                reply_markup=proemny_sub_kb(),
                parse_mode=ParseMode.MARKDOWN
            )
        # Устанавливаем состояние ожидания выбора подтипа
        await state.set_state(OrderForm.sub_install)
    else:
        # Для остальных типов — сразу просим размеры
        if call.message:
            await call.message.answer(
                "📏 Введите ширину изделия (мм)\n*Минимум 150 мм, максимум 3000 мм*",
                parse_mode=ParseMode.MARKDOWN
            )
        await state.set_state(OrderForm.size_w)
    
    # Обязательно подтверждает нажатие кнопки пользователю
    if install_type != "Проёмный":
        await call.answer(text="Переходим к следующему шагу")
    else:
        await call.answer()

@router.callback_query(F.data.startswith("sub_"))
async def set_sub_install(call: CallbackQuery, state: FSMContext):
    sub_map = {
        "Naruzhny": "Наружный",
        "Vnutrenniy": "Внутренний",
        "Vstraivaemy": "Встраиваемый"
    }
    if call.data:
        sub_type = sub_map.get(call.data.split("_")[1], "Неизвестный")
    else:
        sub_type = "Неизвестный"
    
    await state.update_data({"sub_install": sub_type})
    await state.set_state(OrderForm.size_w)
    if call.message:
        try:
            await call.message.answer(f"✅ Подтип '{sub_type}' выбран.\n\nВведите ширину изделия (мм):", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            # Если не удалось отправить сообщение, просто продолжаем
            print(f"Ошибка при отправке сообщения: {e}")
            pass
    await call.answer()

@router.message(OrderForm.size_w)
async def check_width(msg: Message, state: FSMContext):
    try:
        if msg.text:
            width = int(msg.text)
        else:
            await msg.answer("Пожалуйста, введите числовое значение для ширины.")
            return
        if not (150 <= width <= 3000):
            await msg.answer("Ширина должна быть от 150 до 3000 мм.")
            return
        await state.update_data({"size_w": width})
        await state.set_state(OrderForm.size_h)
        try:
            await msg.answer("Введите высоту изделия (мм):", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            # Если не удалось отправить сообщение, просто продолжаем
            logging.error(f"Ошибка при отправке сообщения: {e}")
            pass
    except ValueError:
        await msg.answer("Ошибка: вводите числа.")

@router.message(OrderForm.size_h)
async def check_height(msg: Message, state: FSMContext):
    try:
        if msg.text:
            height = int(msg.text)
        else:
            await msg.answer("Пожалуйста, введите числовое значение для высоты.")
            return
        data = await state.get_data()
        
        # Проверяем наличие width в данных
        if "size_w" not in data:
            await msg.answer("Ошибка: ширина изделия не найдена. Начните оформление заказа заново.")
            return
            
        width = data["size_w"]
        
        if not (150 <= height <= 3000):
            await msg.answer("Высота должна быть от 150 до 3000 мм.")
            return
        
        await state.update_data({"size_h": height})
        
        needs_impost = (width > 1200) or (height > 1200)

        if needs_impost:
            from keyboards import impost_kb
            await msg.answer("⚠️ Размер больше 1200 мм. Хотите поставить импост?", reply_markup=impost_kb())
            await state.set_state(OrderForm.impost)
        else:
            await msg.answer("Введите количество изделий (максимум 30). При необходимости большего количества свяжитесь с менеджером.")
            await state.set_state(OrderForm.qty)
            
    except ValueError:
        await msg.answer("Ошибка: вводите числа.")
        return
    except Exception as e:
        await msg.answer(f"Произошла ошибка: {str(e)}. Начните оформление заказа заново.")
        return

@router.message(OrderForm.qty)
async def confirm_qty(msg: Message, state: FSMContext):
    try:
        if msg.text:
            qty = int(msg.text)
        else:
            await msg.answer("Пожалуйста, введите числовое значение для количества.")
            return
        if qty > 30:
            await msg.answer("Максимум 30 изделий. Для большего количества свяжитесь с менеджером.")
            return
            
        await state.update_data({"qty": qty})
        data = await state.get_data()
        
        # Проверяем наличие install_type в данных
        if "install_type" not in data:
            await msg.answer("Ошибка: тип установки не найден. Начните оформление заказа заново.")
            return
            
        install_type = data["install_type"]

        from keyboards import color_kb
        await msg.answer("Выберите цвет рамы:", reply_markup=color_kb(install_type))
        await state.set_state(OrderForm.color)
        
    except ValueError:
        await msg.answer("Введите числовое значение.")
        return
    except Exception as e:
        await msg.answer(f"Произошла ошибка: {str(e)}. Начните оформление заказа заново.")
        return

@router.callback_query(F.data.startswith("color_"))
async def select_color(call: CallbackQuery, state: FSMContext):
    from keyboards import mounting_kb
    if call.data:
        color = call.data.split("_", 1)[1]  # Используем maxsplit=1 для корректной обработки "Иной цвет по RAL"
    else:
        color = ""
    data = await state.get_data()
    
    if color == "Иной цвет по RAL":
        if call.message:
            await call.message.answer("Введите описание цвета (код или название):")
        await state.set_state(OrderForm.color_description)
        data["color"] = color
        await state.update_data(data)
    else:
        await state.update_data({"color": color})
        if call.message:
            await call.message.answer("Выберите способ крепления:", reply_markup=mounting_kb())
        await state.set_state(OrderForm.mount)

@router.message(OrderForm.color_description)
async def save_ral_color(msg: Message, state: FSMContext):
    data = await state.get_data()
    # Сохраняем полное описание RAL цвета
    ral_description = f"Иной цвет по RAL ({msg.text})"
    data["color"] = ral_description
    await state.update_data(data)

    from keyboards import mounting_kb
    await msg.answer("Выберите способ крепления:", reply_markup=mounting_kb())
    await state.set_state(OrderForm.mount)

@router.callback_query(F.data.startswith("mount_"))
async def select_mounting(call: CallbackQuery, state: FSMContext):
    from keyboards import fabric_kb
    
    mount_map = {
        "mount_Z": "Z-кронштейны",
        "mount_Metal": "Металл зацепы",
        "mount_Plastic": "Пластик зацепы",
        "mount_Default": "По умолчанию"
    }
    
    if call.data:
        mount_key = call.data
        mount_value = mount_map.get(mount_key, mount_key)
    else:
        mount_value = "Неизвестный"
    
    await state.update_data({"mount": mount_value})
    if call.message:
        await call.message.answer("Выберите тип полотна:", reply_markup=fabric_kb())
    await state.set_state(OrderForm.fabric)
    await call.answer()

@router.callback_query(F.data == "impost_No")
async def choose_impost_no(call: CallbackQuery, state: FSMContext):
    from keyboards import fabric_kb

    if call.message:
        await call.message.answer("Без импоста. Переходим к следующим настройкам.")
    await state.update_data({"impost": "no"})

    if call.message:
        await call.message.answer("Выберите тип полотна:", reply_markup=fabric_kb())

    await state.set_state(OrderForm.fabric)
    await call.answer()

@router.callback_query(F.data == "impost_Yes")
async def choose_impost_yes(call: CallbackQuery, state: FSMContext):
    from keyboards import orient_impost_kb
    if call.message:
        await call.message.answer("Как установить импост?")
        await call.message.answer("", reply_markup=orient_impost_kb())
    await state.update_data({"impost": "yes"})
    await state.set_state(OrderForm.orient)
    await call.answer()

@router.callback_query(F.data.startswith("orient_"))
async def orient_impost(call: CallbackQuery, state: FSMContext):
    orient = "Вертикально" if call.data == "orient_Vertical" else "Горизонтально"
    await state.update_data({"orient": orient})
    from keyboards import fabric_kb
    if call.message:
        await call.message.answer("Выберите тип полотна:", reply_markup=fabric_kb())
    await state.set_state(OrderForm.fabric)
    await call.answer()

@router.callback_query(F.data.startswith("fabric_"))
async def select_fabric(call: CallbackQuery, state: FSMContext):
    if call.data:
        fabric = call.data.split("_")[1]
    else:
        fabric = ""
    await state.update_data({"fabric": fabric})
    from keyboards import date_kb
    
    next_day = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
    if call.message:
        await call.message.answer(f"Желаемый срок готовности:\n*Дата {next_day}*", parse_mode=ParseMode.MARKDOWN)
        await call.message.answer("", reply_markup=date_kb())
    await state.set_state(OrderForm.finish_date)
    await call.answer()

@router.callback_query(F.data.startswith("date_select_"))
async def finish_date_select(call: CallbackQuery, state: FSMContext):
    from keyboards import date_kb
    from datetime import datetime
    
    # Извлекаем выбранную дату из callback_data
    if call.data:
        selected_date_str = call.data.replace("date_select_", "")
    else:
        selected_date_str = ""
    
    # Проверяем формат даты и валидируем
    try:
        selected_date = datetime.strptime(selected_date_str, "%d.%m.%Y").date()
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        
        # Проверяем, что дата не раньше чем завтра
        if selected_date < tomorrow:
            await call.answer("Нельзя выбрать дату ранее, чем завтра!", show_alert=True)
            return
        
        await state.update_data({"finish_date": selected_date_str})
        if call.message:
            await call.message.answer(f"📅 Желаемый срок готовности установлен: {selected_date_str}\n\nНапишите примечание к заказу (можно оставить пустым)")
        await state.set_state(OrderForm.notes)
    except ValueError:
        await call.answer("Неверный формат даты!", show_alert=True)

@router.callback_query(F.data.startswith("date_nav_"))
async def navigate_calendar(call: CallbackQuery, state: FSMContext):
    from keyboards import date_kb
    from datetime import datetime
    
    # Проверяем, что callback_data существует
    if not call.data:
        await call.answer("Ошибка при навигации по календарю", show_alert=True)
        return
    
    # Извлекаем год и месяц из callback_data
    parts = call.data.split("_")
    if len(parts) >= 4:  # date_nav_year_month
        try:
            year = int(parts[2])
            month = int(parts[3])
            
            # Корректируем месяц если нужно
            if month == 0:
                month = 12
                year -= 1
            elif month == 13:
                month = 1
                year += 1
            
            # Создаем новую дату
            new_date = datetime(year, month, 1)
            
            # Обновляем клавиатуру
            try:
                if call.message:
                    await call.message.edit_reply_markup(reply_markup=date_kb(new_date))
            except Exception as e:
                # Если не можем редактировать сообщение, просто игнорируем ошибку
                print(f"Ошибка при редактировании клавиатуры: {e}")
                pass
        except (ValueError, IndexError):
            await call.answer("Ошибка при навигации по календарю", show_alert=True)
    else:
        await call.answer("Ошибка при навигации по календарю", show_alert=True)


@router.callback_query(F.data == "date_ignore")
async def ignore_date_button(call: CallbackQuery):
    # Просто игнорируем нажатие на заголовочные кнопки
    await call.answer()

@router.message(OrderForm.notes)
async def save_notes(msg: Message, state: FSMContext):
    from keyboards import confirm_order_kb
    data = await state.get_data()
    data["notes"] = msg.text

    total_price = 0 # Здесь вызывайте функцию расчета цены

    price_msg = (f"📋 **Смета заказа**:\n\n"
                 f"Тип: {data['install_type']}\n"
                 f"Размер: {data['size_w']}x{data['size_h']} мм\n"
                 f"Количество: {data['qty']}\n"
                 f"Цвет: {data['color']}\n"
                 f"Импост: {data['impost']}\n"
                 f"Полотно: {data['fabric']}\n\n"
                 f"💰 **Цена: {total_price} руб.**\n\nПодтвердить заказ?")

    await msg.answer(price_msg, reply_markup=confirm_order_kb(), parse_mode=ParseMode.MARKDOWN)
    await state.set_state(OrderForm.summary)

@router.callback_query(F.data == "confirm_order")
async def send_confirmation(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # client_name = data.get("client_name", "Клиент")  # Не используется
    
    # Сохранение в Google Sheet
    order_id = f"ORD-{len(str(data))}"
    from google_sheets import save_order_to_sheet
    await save_order_to_sheet(order_id, data)
    
    if call.message:
        await call.message.answer(f"✅ Заказ #{order_id} принят.")
    await state.clear()

@router.callback_query(F.data == "cancel_order")
async def cancel_order(call: CallbackQuery, state: FSMContext):
    await state.clear()
    if call.message:
        await call.message.answer("Заявка отменена.")