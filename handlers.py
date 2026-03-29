from datetime import datetime

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from config import BotProfile
from sheets import append_to_sheet
from states import BloodPressure

confirm_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✅ Подтвердить"), KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True,
)

skip_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Пропустить")]],
    resize_keyboard=True,
)

UNAUTHORIZED_MESSAGE = "Сорян, у тебя нет доступа"


def create_router(profile: BotProfile) -> Router:
    router = Router()

    def is_authorized(message: types.Message) -> bool:
        if not profile.has_owner_restriction:
            return True
        return bool(message.from_user and message.from_user.id == profile.telegram_id)

    @router.message(lambda message: not is_authorized(message))
    async def reject_unauthorized(message: types.Message):
        await message.answer(UNAUTHORIZED_MESSAGE)

    @router.message(Command("get_id"), is_authorized)
    async def get_id(message: types.Message):
        await message.answer(f"ID этого чата: {message.chat.id}\nТвой Telegram ID: {message.from_user.id}")

    @router.message(Command("start"), is_authorized)
    async def cmd_start(message: types.Message):
        await message.answer(
            f"Привет! Я бот для записи давления.\nПрофиль: {profile.name}\nИспользуй /add, чтобы начать."
        )

    @router.message(Command("ref"), is_authorized)
    async def cmd_ref(message: types.Message):
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{profile.spreadsheet_id}/edit"
        await message.answer(f"Твоя Google-таблица:\n{spreadsheet_url}")

    @router.message(Command("cancel"), is_authorized)
    @router.message(F.text.casefold() == "отмена", is_authorized)
    async def cmd_cancel(message: types.Message, state: FSMContext):
        await state.clear()
        await message.answer("Ввод отменен.", reply_markup=ReplyKeyboardRemove())

    @router.message(Command("add"), is_authorized)
    async def start_add(message: types.Message, state: FSMContext):
        await state.set_state(BloodPressure.waiting_for_systolic)
        await message.answer(
            "Введите верхнее (систолическое) давление:",
            reply_markup=ReplyKeyboardRemove(),
        )

    @router.message(BloodPressure.waiting_for_systolic, is_authorized)
    async def process_systolic(message: types.Message, state: FSMContext):
        if not message.text.isdigit():
            return await message.answer("Пожалуйста, введите число!")
        await state.update_data(systolic=message.text)
        await state.set_state(BloodPressure.waiting_for_diastolic)
        await message.answer("Введите нижнее (диастолическое) давление:")

    @router.message(BloodPressure.waiting_for_diastolic, is_authorized)
    async def process_diastolic(message: types.Message, state: FSMContext):
        if not message.text.isdigit():
            return await message.answer("Пожалуйста, введите число!")
        await state.update_data(diastolic=message.text)
        await state.set_state(BloodPressure.waiting_for_pulse)
        await message.answer(
            "Введите пульс (или нажмите кнопку 'Пропустить'):",
            reply_markup=skip_kb,
        )

    @router.message(BloodPressure.waiting_for_pulse, is_authorized)
    async def process_pulse(message: types.Message, state: FSMContext):
        pulse = message.text if message.text.isdigit() else "—"
        data = await state.update_data(pulse=pulse)

        summary = f"📊 Данные: {data['systolic']}/{data['diastolic']}\n💓 Пульс: {data['pulse']}"
        await state.set_state(BloodPressure.waiting_for_confirm)
        await message.answer(f"{summary}\n\nВсе верно?", reply_markup=confirm_kb)

    @router.message(BloodPressure.waiting_for_confirm, F.text == "❌ Отмена", is_authorized)
    async def process_cancel_confirm(message: types.Message, state: FSMContext):
        await state.clear()
        await message.answer("Запись отменена.", reply_markup=ReplyKeyboardRemove())

    @router.message(BloodPressure.waiting_for_confirm, F.text == "✅ Подтвердить", is_authorized)
    async def process_confirm(message: types.Message, state: FSMContext):
        user_data = await state.get_data()
        now = datetime.now()

        row = [
            now.strftime("%d.%m.%Y"),
            now.strftime("%H:%M"),
            user_data["systolic"],
            user_data["diastolic"],
            user_data["pulse"],
        ]

        try:
            append_to_sheet(
                data=row,
                spreadsheet_id=profile.spreadsheet_id,
                service_account_file=profile.service_account_path,
            )

            report_text = (
                f"🩺 <b>Новая запись давления</b>\n\n"
                f"👤 Профиль: <b>{profile.name}</b>\n"
                f"📈 Давление: <b>{row[2]}/{row[3]}</b>\n"
                f"💓 Пульс: {row[4]}\n"
                f"🕒 Время: {row[1]}"
            )

            if profile.group_id is not None:
                await message.bot.send_message(
                    chat_id=profile.group_id,
                    text=report_text,
                    parse_mode="HTML",
                )

            await message.answer("✅ Данные успешно сохранены!", reply_markup=ReplyKeyboardRemove())
        except Exception as exc:
            await message.answer(
                f"❌ Ошибка при сохранении: {exc}",
                reply_markup=ReplyKeyboardRemove(),
            )
            print(f"Ошибка сохранения для профиля {profile.name}: {exc}")
        finally:
            await state.clear()

    return router
