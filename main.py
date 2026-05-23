import asyncio
import logging
from collections import defaultdict

from aiogram import Bot, Dispatcher

import config
from handlers import create_router, create_unauthorized_router


async def run_bot_profiles(bot_token: str, profiles: list[config.BotProfile]):
    bot = Bot(token=bot_token)
    dp = Dispatcher()

    for profile in profiles:
        dp.include_router(create_router(profile))

    dp.include_router(create_unauthorized_router(profiles))

    logging.info(
        "Запуск бота для профилей: %s",
        ", ".join(profile.name for profile in profiles),
    )

    await dp.start_polling(bot, handle_signals=False)


async def main():
    logging.basicConfig(level=logging.INFO)

    profiles_by_token: dict[str, list[config.BotProfile]] = defaultdict(list)
    for profile in config.BOT_PROFILES:
        profiles_by_token[profile.bot_token].append(profile)

    tasks = [
        asyncio.create_task(
            run_bot_profiles(bot_token, profiles),
            name=f"bot:{','.join(profile.name for profile in profiles)}",
        )
        for bot_token, profiles in profiles_by_token.items()
    ]

    print(f"Polling-сессий запущено: {len(tasks)}")
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
