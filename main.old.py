import logging
import sys
import signal

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
log = logging.getLogger(__name__)

bot = Bot(Config())


async def run():
    await init_database(
        f"mysql://{bot.config.db_user}:{bot.config.db_passwd}"
        f"@{bot.config.db_url}/{bot.config.db_name}"
    )

    if status := bot.config.status:
        bot.activity = Activity(name=status, type=bot.config.status_type)

    load_locales(bot.locale_cache)
    bot.load_cogs()

    await bot.generate_prefix_cache()
    await bot.generate_moderator_cache()
    await bot.generate_locale_cache()

    await bot.login(token=bot.config.token)
    await bot.connect()


def sigterm_handler(signum, frame):
    log.info("Received SIGTERM, exiting gracefully...")
    raise KeyboardInterrupt


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    signal.signal(signal.SIGTERM, sigterm_handler)

    try:
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        loop.run_until_complete(Tortoise.close_connections())
        loop.run_until_complete(bot.logout())
    finally:
        loop.close()
