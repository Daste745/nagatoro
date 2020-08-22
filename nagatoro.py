import logging

import nagatoro
from nagatoro.objects import Config


logger = logging.getLogger()
logger.setLevel(logging.INFO)
# TODO: Implement custom logging format.
# formatter = logging.Formatter(
#     "[%(levelname)s] %(asctime)s - %(name)s: %(message)s")

with open("data/config.json") as file:
    config = Config.from_file(file)

bot = nagatoro.Bot(config, heartbeat_timeout=30)

if __name__ == "__main__":
    bot.startup()
