import logging

import asyncio
from tortoise import Tortoise
from discord import Activity, ActivityType

from nagatoro import Bot
from nagatoro.objects import Config
from nagatoro.db import init_database


logger = logging.getLogger()
logger.setLevel(logging.INFO)
# TODO: Implement custom logging format.
# formatter = logging.Formatter(
#     "[%(levelname)s] %(asctime)s - %(name)s: %(message)s")

with open("data/config.json") as file:
    # TODO: Use environmental variables instead of a config file
    config = Config.from_file(file)

db_url = f"mysql://{config.db_user}:{config.db_passwd}@{config.db_url}/{config.db_name}"
bot = Bot(config)


async def run():
    await init_database(db_url)

    if not bot.config.testing:
        bot.activity = Activity(
            name=f"{bot.config.prefix}help", type=ActivityType.watching
        )
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
