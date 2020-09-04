import logging

import asyncio
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
    config = Config.from_file(file)

bot = Bot(config)


async def run():
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
        loop.run_until_complete(init_database())
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        loop.run_until_complete(bot.logout())
    finally:
        loop.close()
