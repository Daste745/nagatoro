import logging

import asyncio
from tortoise import Tortoise
from discord import Activity

from nagatoro import Bot
from nagatoro.objects import Config
from nagatoro.db import init_database


logger = logging.getLogger()
logger.setLevel(logging.INFO)
# TODO: Implement custom logging format.
# formatter = logging.Formatter(
#     "[%(levelname)s] %(asctime)s - %(name)s: %(message)s")

bot = Bot(Config())
db_url = (
    f"mysql://{bot.config.db_user}:{bot.config.db_passwd}"
    f"@{bot.config.db_url}/{bot.config.db_name}"
)


async def run():
    await init_database(db_url)

    if status := bot.config.status:
        bot.activity = Activity(name=status, type=bot.config.status_type)
    bot.load_cogs()
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
