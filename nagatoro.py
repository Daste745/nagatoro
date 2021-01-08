import logging
import sys

import asyncio
from tortoise import Tortoise
from discord import Activity

from nagatoro import Bot
from nagatoro.objects import Config
from nagatoro.db import init_database
from nagatoro.utils import load_locales


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(funcName)s:%(message)s",
)

bot = Bot(Config())
db_url = (
    f"mysql://{bot.config.db_user}:{bot.config.db_passwd}"
    f"@{bot.config.db_url}/{bot.config.db_name}"
)


async def run():
    await init_database(db_url)

    if status := bot.config.status:
        bot.activity = Activity(name=status, type=bot.config.status_type)

    load_locales(bot.locale_cache)
    bot.load_cogs()

    await bot.generate_prefix_cache()
    await bot.generate_moderator_cache()
    await bot.generate_locale_cache()

    await bot.login(token=bot.config.token)
    await bot.connect()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        loop.run_until_complete(Tortoise.close_connections())
        loop.run_until_complete(bot.logout())
    finally:
        loop.close()
