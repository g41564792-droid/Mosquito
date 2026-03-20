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
    size_all = State()  # новое состояние для ввода всех размеров и количества
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
                "📏 Введите размеры: ширина высота [кол-во]\n"
                "Например: 800 1200 2\n"
                "*Минимум 150 мм, максимум 3000 мм. Количество по умолчанию 1, максимум 30.*",
                parse_mode=ParseMode.MARKDOWN
            )
        await state.set_state(OrderForm.size_all)
    
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
    await state.set_state(OrderForm.size_all)
    if call.message:
        try:
            await call.message.answer(
                f"✅ Подтип '{sub_type}' выбран.\n\n"
                "📏 Введите размеры: ширина высота [кол-во]\n"
                "Например: 800 1200 2\n"
                "*Минимум 150 мм, максимум 3000 мм. Количество по умолчанию 1, максимум 30.*",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            # Если не удалось отправить сообщение, просто продолжаем
            print(f"Ошибка при отправке сообщения: {e}")
            pass
    await call.answer()

@router.message(OrderForm.size_all)
async def process_size_all(msg: Message, state: FSMContext):
    """
    Обработчик ввода размеров и количества в одном сообщении.
    Формат: ширина высота [кол-во]
    Пример: 800 1200 2
    """
    try:
        if not msg.text:
            await msg.answer("Пожалуйста, введите размеры.")
            return
        
        parts = msg.text.strip().split()
        if len(parts) not in (2, 3):
            await msg.answer(
                "Неверный формат. Введите ширина высота [кол-во]\n"
                "Например: 800 1200 2"
            )
            return
        
        width = int(parts[0])
        height = int(parts[1])
        qty = int(parts[2]) if len(parts) == 3 else 1
        
        # Проверка диапазонов
        if not (150 <= width <= 3000):
            await msg.answer("Ширина должна быть от 150 до 3000 мм.")
            return
        if not (150 <= height <= 3000):
            await msg.answer("Высота должна быть от 150 до 3000 мм.")
            return
        if qty > 30:
            await msg.answer("Максимум 30 изделий. Для большего количества свяжитесь с менеджером.")
            return
        if qty < 1:
            await msg.answer("Количество должно быть положительным.")
            return
        
        # Получаем текущий список размеров
        data = await state.get_data()
        sizes = data.get("sizes", [])
        # Добавляем новый размер
        sizes.append({"width": width, "height": height, "qty": qty})
        # Сохраняем обновленный список и также отдельные поля для обратной совместимости
        await state.update_data({
            "sizes": sizes,
            "size_w": width,
            "size_h": height,
            "qty": qty
        })
        
        # Проверяем, нужен ли импост для этого размера
        needs_impost = (width > 1200) or (height > 1200)
        if needs_impost:
            from keyboards import impost_kb
            await msg.answer("⚠️ Размер больше 1200 мм. Хотите поставить импост?", reply_markup=impost_kb())
            await state.set_state(OrderForm.impost)
        else:
            # Сообщение с кнопками
            from keyboards import size_action_kb
            await msg.answer(
                f"✅ Данные сохранены: ширина {width} мм, высота {height} мм, количество {qty}.\n"
                f"Всего размеров: {len(sizes)}.",
                reply_markup=size_action_kb()
            )
            
    except ValueError:
        await msg.answer("Ошибка: вводите числа.")
    except Exception as e:
        logging.error(f"Ошибка в process_size_all: {e}", exc_info=True)
        await msg.answer("Произошла ошибка. Начните оформление заказа заново.")

@router.callback_query(F.data == "size_action_add")
async def add_more_sizes(call: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Добавить еще размеры'"""
    if call.message:
        await call.message.answer(
            "📏 Введите следующие размеры: ширина высота [кол-во]\n"
            "Например: 800 1200 2\n"
            "*Минимум 150 мм, максимум 3000 мм. Количество по умолчанию 1, максимум 30.*",
            parse_mode=ParseMode.MARKDOWN
        )
    await state.set_state(OrderForm.size_all)
    await call.answer()

@router.callback_query(F.data == "size_action_next")
async def proceed_to_next(call: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Дальше к оформлению'"""
    data = await state.get_data()
    sizes = data.get("sizes", [])
    if not sizes:
        if call.message:
            await call.message.answer("Ошибка: нет сохраненных размеров. Введите размеры.")
            await state.set_state(OrderForm.size_all)
        await call.answer()
        return
    
    # Если импост уже задан, переходим к следующему шагу в зависимости от его значения
    impost = data.get("impost")
    if impost is not None:
        if impost == "yes" and not data.get("orient"):
            # Нужно выбрать ориентацию импоста
            from keyboards import orient_impost_kb
            if call.message:
                await call.message.answer("Как установить импост?", reply_markup=orient_impost_kb())
            await state.set_state(OrderForm.orient)
        else:
            # Импост не нужен или уже выбран, переходим к выбору цвета
            install_type = data.get("install_type")
            if not install_type:
                if call.message:
                    await call.message.answer("Ошибка: тип установки не найден. Начните оформление заказа заново.")
                await state.clear()
                await call.answer()
                return
            from keyboards import color_kb
            if call.message:
                await call.message.answer("Выберите цвет рамы:", reply_markup=color_kb(install_type))
            await state.set_state(OrderForm.color)
    else:
        # Импост еще не задан, проверяем, нужен ли он
        needs_impost = False
        for size in sizes:
            if size["width"] > 1200 or size["height"] > 1200:
                needs_impost = True
                break
        
        if needs_impost:
            from keyboards import impost_kb
            if call.message:
                await call.message.answer("⚠️ Один из размеров больше 1200 мм. Хотите поставить импост?", reply_markup=impost_kb())
            await state.set_state(OrderForm.impost)
        else:
            # Переходим к выбору цвета
            install_type = data.get("install_type")
            if not install_type:
                if call.message:
                    await call.message.answer("Ошибка: тип установки не найден. Начните оформление заказа заново.")
                await state.clear()
                await call.answer()
                return
            from keyboards import color_kb
            if call.message:
                await call.message.answer("Выберите цвет рамы:", reply_markup=color_kb(install_type))
            await state.set_state(OrderForm.color)
    
    await call.answer()


@router.callback_query(F.data.startswith("color_"))
async def select_color(call: CallbackQuery, state: FSMContext):
    from keyboards import mounting_kb
    if call.data:
        color = call.data.split("_", 1)[1]  # Используем maxsplit=1 для корректной обработки "Цвет по RAL"
    else:
        color = ""
    data = await state.get_data()
    
    if color == "Цвет по RAL":
        if call.message:
            await call.message.answer("Введите 4 цифры цвета по каталогу RAL (например, 9016):")
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
    ral_description = f"Цвет по RAL ({msg.text})"
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
    await state.update_data({"impost": "no"})
    if call.message:
        await call.message.answer("✅ Импост не требуется.")
        # Показываем кнопки для добавления размеров или продолжения
        from keyboards import size_action_kb
        data = await state.get_data()
        sizes = data.get("sizes", [])
        await call.message.answer(
            f"Всего размеров: {len(sizes)}.",
            reply_markup=size_action_kb()
        )
    await state.set_state(OrderForm.size_all)
    await call.answer()

@router.callback_query(F.data == "impost_Yes")
async def choose_impost_yes(call: CallbackQuery, state: FSMContext):
    from keyboards import orient_impost_kb
    logging.debug("impost_Yes triggered")
    try:
        kb = orient_impost_kb()
        logging.debug(f"Keyboard created: {kb}")
        if call.message:
            await call.message.answer("Как установить импост?", reply_markup=kb)
        else:
            logging.warning("call.message is None")
        await state.update_data({"impost": "yes"})
        await state.set_state(OrderForm.orient)
    except Exception as e:
        logging.error(f"Error in impost_Yes: {e}", exc_info=True)
        if call.message:
            await call.message.answer("Произошла ошибка. Пожалуйста, попробуйте ещё раз.")
    await call.answer()

@router.callback_query(F.data.startswith("orient_"))
async def orient_impost(call: CallbackQuery, state: FSMContext):
    logging.debug(f"orient_impost triggered with {call.data}")
    orient = "Вертикально" if call.data == "orient_Vertical" else "Горизонтально"
    await state.update_data({"orient": orient})
    # Показываем кнопки для добавления размеров или продолжения
    from keyboards import size_action_kb
    data = await state.get_data()
    sizes = data.get("sizes", [])
    if call.message:
        try:
            await call.message.answer(f"✅ Импост установлен ({orient}).")
            kb = size_action_kb()
            await call.message.answer(
                f"Всего размеров: {len(sizes)}.",
                reply_markup=kb
            )
        except Exception as e:
            logging.error(f"Error sending messages in orient_impost: {e}", exc_info=True)
    else:
        logging.warning("call.message is None in orient_impost")
    await state.set_state(OrderForm.size_all)
    await call.answer()

@router.callback_query(F.data.startswith("fabric_"))
async def select_fabric(call: CallbackQuery, state: FSMContext):
    fabric_map = {
        "Standard": "Стандартное",
        "Antipyl": "Антипыль",
        "Antimoska": "Антимошка",
        "Antikoshka": "Антикошка"
    }
    
    if call.data:
        fabric_key = call.data.split("_")[1]
        fabric = fabric_map.get(fabric_key, fabric_key)
    else:
        fabric = ""
    
    await state.update_data({"fabric": fabric})
    from keyboards import date_kb
    
    next_day = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
    if call.message:
        await call.message.answer(
            f"📅 *Желаемый срок готовности*\n\n"
            f"По умолчанию: *{next_day}* (завтра).\n"
            f"Вы можете:\n"
            f"• Выбрать дату из календаря ниже\n"
            f"• Нажать кнопку '📝 Ввести дату вручную' и отправить дату в формате *ДД.ММ.ГГГГ*\n"
            f"• Выбрать дату позже завтрашнего дня",
            reply_markup=date_kb(),
            parse_mode=ParseMode.MARKDOWN
        )
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

@router.callback_query(F.data == "date_manual")
async def manual_date_input(call: CallbackQuery, state: FSMContext):
    if call.message:
        await call.message.answer(
            "📝 Введите дату вручную в формате *ДД.ММ.ГГГГ* (например, 25.12.2024).\n"
            "Дата должна быть не раньше завтрашнего дня.",
            parse_mode=ParseMode.MARKDOWN
        )
    await call.answer()

@router.message(OrderForm.finish_date)
async def process_finish_date_text(msg: Message, state: FSMContext):
    from datetime import datetime
    date_text = msg.text.strip()
    try:
        selected_date = datetime.strptime(date_text, "%d.%m.%Y").date()
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        if selected_date < tomorrow:
            await msg.answer("❌ Нельзя выбрать дату ранее, чем завтра! Пожалуйста, введите корректную дату.")
            return
        await state.update_data({"finish_date": date_text})
        await msg.answer(f"📅 Желаемый срок готовности установлен: {date_text}\n\nНапишите примечание к заказу (можно оставить пустым)")
        await state.set_state(OrderForm.notes)
    except ValueError:
        await msg.answer("❌ Неверный формат даты! Введите дату в формате ДД.ММ.ГГГГ (например, 25.12.2024).")

@router.message(OrderForm.notes)
async def save_notes(msg: Message, state: FSMContext):
    from keyboards import confirm_order_kb
    try:
        # Сохраняем примечание в состоянии
        await state.update_data({"notes": msg.text})
        # Получаем актуальные данные
        data = await state.get_data()

        # Безопасное извлечение данных с значениями по умолчанию
        install_type = data.get("install_type", "не указан")
        sizes = data.get("sizes", [])
        color = data.get("color", "не выбран")
        impost = data.get("impost", "нет")
        fabric = data.get("fabric", "не выбран")
        orient = data.get("orient", "")
        sub_install = data.get("sub_install", "")

        # Формируем строку импоста с ориентацией если есть
        impost_str = impost
        if impost == "yes" and orient:
            impost_str = f"да ({orient})"
        elif impost == "no":
            impost_str = "нет"

        # Формируем строку размеров
        if sizes:
            size_lines = []
            total_qty = 0
            for idx, size in enumerate(sizes, 1):
                size_lines.append(f"{idx}. {size['width']}x{size['height']} мм — {size['qty']} шт.")
                total_qty += size['qty']
            sizes_text = "\n".join(size_lines)
            total_qty_text = f"Всего изделий: {total_qty}"
        else:
            sizes_text = "Нет размеров"
            total_qty_text = ""

        total_price = 0 # Здесь вызывайте функцию расчета цены

        price_msg = (f"📋 **Смета заказа**:\n\n"
                     f"Тип: {install_type}\n"
                     f"Подтип: {sub_install if sub_install else 'не применимо'}\n"
                     f"Размеры:\n{sizes_text}\n"
                     f"{total_qty_text}\n"
                     f"Цвет: {color}\n"
                     f"Импост: {impost_str}\n"
                     f"Полотно: {fabric}\n\n"
                     f"💰 **Цена: {total_price} руб.**\n\nПодтвердить заказ?")

        await msg.answer(price_msg, reply_markup=confirm_order_kb(), parse_mode=ParseMode.MARKDOWN)
        await state.set_state(OrderForm.summary)
    except Exception as e:
        logging.error(f"Ошибка в save_notes: {e}", exc_info=True)
        await msg.answer("Произошла ошибка при формировании сводки. Пожалуйста, начните заказ заново.")
        await state.clear()

@router.callback_query(F.data == "confirm_order")
async def send_confirmation(call: CallbackQuery, state: FSMContext):
    import asyncio
    from datetime import datetime
    data = await state.get_data()
    
    # Генерация order_id на основе временной метки
    order_id = f"ORD-{int(datetime.now().timestamp())}"
    
    # Сохранение в Google Sheet через отдельный поток, чтобы не блокировать event loop
    from google_sheets import save_order_to_sheet
    try:
        await asyncio.to_thread(save_order_to_sheet, order_id, data)
    except Exception as e:
        logging.error(f"Ошибка при сохранении заказа: {e}", exc_info=True)
        if call.message:
            await call.message.answer(f"❌ Ошибка при сохранении заказа: {str(e)[:200]}")
        return
    
    if call.message:
        await call.message.answer(f"✅ Заказ #{order_id} принят.")
    await state.clear()

@router.callback_query(F.data == "cancel_order")
async def cancel_order(call: CallbackQuery, state: FSMContext):
    await state.clear()
    if call.message:
        await call.message.answer("Заявка отменена.")