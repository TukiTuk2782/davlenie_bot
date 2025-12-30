import asyncio
import logging
from aiogram import Bot, Dispatcher
import config  # Импортируем весь наш файл config.py
from handlers import router


async def main():
    logging.basicConfig(level=logging.INFO)

    # Обращаемся именно так: config.BOT_TOKEN
    bot = Bot(token=config.BOT_TOKEN)

    dp = Dispatcher()
    dp.include_router(router)

    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())