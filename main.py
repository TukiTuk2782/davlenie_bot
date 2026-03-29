import asyncio
import logging

from aiogram import Bot, Dispatcher

import config
from handlers import create_router


async def run_profile_bot(profile: config.BotProfile):
    bot = Bot(token=profile.bot_token)
    dp = Dispatcher()
    dp.include_router(create_router(profile))

    logging.info(
        "Запуск профиля '%s' (telegram_id=%s, owner_restricted=%s)",
        profile.name,
        profile.telegram_id,
        profile.has_owner_restriction,
    )

    await dp.start_polling(bot, handle_signals=False)


async def main():
    logging.basicConfig(level=logging.INFO)

    tasks = [
        asyncio.create_task(run_profile_bot(profile), name=f"bot:{profile.name}")
        for profile in config.BOT_PROFILES
    ]

    print(f"Ботов запущено: {len(tasks)}")
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
