import config  # Правильный импорт всего модуля
from datetime import datetime
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from states import BloodPressure
from sheets import append_to_sheet

router = Router()

# --- КЛАВИАТУРЫ ---
confirm_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✅ Подтвердить"), KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True
)

skip_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Пропустить")]],
    resize_keyboard=True
)

# --- ХЕНДЛЕРЫ ---

@router.message(Command("get_id"))
async def get_id(message: types.Message):
    await message.answer(f"ID этого чата: {message.chat.id}")

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот для записи давления. Используй /add, чтобы начать.")

@router.message(Command("cancel"))
@router.message(F.text.casefold() == "отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Ввод отменен.", reply_markup=ReplyKeyboardRemove())

@router.message(Command("add"))
async def start_add(message: types.Message, state: FSMContext):
    await state.set_state(BloodPressure.waiting_for_systolic)
    await message.answer("Введите верхнее (систолическое) давление:", reply_markup=ReplyKeyboardRemove())

@router.message(BloodPressure.waiting_for_systolic)
async def process_systolic(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Пожалуйста, введите число!")
    await state.update_data(systolic=message.text)
    await state.set_state(BloodPressure.waiting_for_diastolic)
    await message.answer("Введите нижнее (диастолическое) давление:")

@router.message(BloodPressure.waiting_for_diastolic)
async def process_diastolic(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Пожалуйста, введите число!")
    await state.update_data(diastolic=message.text)
    await state.set_state(BloodPressure.waiting_for_pulse)
    await message.answer("Введите пульс (или нажмите кнопку 'Пропустить'):", reply_markup=skip_kb)

@router.message(BloodPressure.waiting_for_pulse)
async def process_pulse(message: types.Message, state: FSMContext):
    # Если нажата кнопка или введено не число — пульс будет пустым
    pulse = message.text if message.text.isdigit() else "—"
    data = await state.update_data(pulse=pulse)

    summary = f"📊 Данные: {data['systolic']}/{data['diastolic']}\n💓 Пульс: {data['pulse']}"
    await state.set_state(BloodPressure.waiting_for_confirm)
    await message.answer(f"{summary}\n\nВсе верно?", reply_markup=confirm_kb)

@router.message(BloodPressure.waiting_for_confirm, F.text == "❌ Отмена")
async def process_cancel_confirm(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Запись отменена.", reply_markup=ReplyKeyboardRemove())

@router.message(BloodPressure.waiting_for_confirm, F.text == "✅ Подтвердить")
async def process_confirm(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    now = datetime.now()

    # Данные для Google Таблицы
    row = [
        now.strftime("%d.%m.%Y"), # Дата
        now.strftime("%H:%M"),    # Время
        user_data['systolic'],
        user_data['diastolic'],
        user_data['pulse']
    ]

    try:
        # 1. Запись в таблицу
        append_to_sheet(row)

        # 2. Формируем отчет для группы (используем HTML для надежности)
        report_text = (
            f"🩺 <b>Новая запись давления</b>\n\n"
            f"📈 Давление: <b>{row[2]}/{row[3]}</b>\n"
            f"💓 Пульс: {row[4]}\n"
            f"🕒 Время: {row[1]}"
        )

        # 3. Отправка в группу через config.GROUP_ID
        await message.bot.send_message(
            chat_id=config.GROUP_ID,
            text=report_text,
            parse_mode="HTML"
        )

        await message.answer("✅ Данные успешно сохранены!", reply_markup=ReplyKeyboardRemove())

    except Exception as e:
        await message.answer(f"❌ Ошибка при сохранении: {e}", reply_markup=ReplyKeyboardRemove())
        print(f"Ошибка сохранения: {e}")

    finally:
        await state.clear()