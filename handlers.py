from datetime import datetime
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from states import BloodPressure
from sheets import append_to_sheet

router = Router()

# Клавиатуры (можно вынести в отдельный kb.py, если их станет много)
confirm_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✅ Подтвердить"), KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True
)
skip_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Пропустить")]],
    resize_keyboard=True
)


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
    await message.answer("Введите верхнее давление:", reply_markup=ReplyKeyboardRemove())


@router.message(BloodPressure.waiting_for_systolic)
async def process_systolic(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Введите число!")
    await state.update_data(systolic=message.text)
    await state.set_state(BloodPressure.waiting_for_diastolic)
    await message.answer("Введите нижнее давление:")


@router.message(BloodPressure.waiting_for_diastolic)
async def process_diastolic(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Введите число!")
    await state.update_data(diastolic=message.text)
    await state.set_state(BloodPressure.waiting_for_pulse)
    await message.answer("Введите пульс (или нажмите кнопку):", reply_markup=skip_kb)


@router.message(BloodPressure.waiting_for_pulse)
async def process_pulse(message: types.Message, state: FSMContext):
    pulse = message.text if message.text.isdigit() else ""
    data = await state.update_data(pulse=pulse)

    summary = f"Данные: {data['systolic']}/{data['diastolic']}, Пульс: {data['pulse'] or '-'}"
    await state.set_state(BloodPressure.waiting_for_confirm)
    await message.answer(f"{summary}\nВсе верно?", reply_markup=confirm_kb)


@router.message(BloodPressure.waiting_for_confirm, F.text == "✅ Подтвердить")
async def process_confirm(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    now = datetime.now()

    row = [now.strftime("%Y-%m-%d"), now.strftime("%H:%M"),
           user_data['systolic'], user_data['diastolic'], user_data['pulse']]

    append_to_sheet(row)
    await state.clear()
    await message.answer("Сохранено!", reply_markup=ReplyKeyboardRemove())