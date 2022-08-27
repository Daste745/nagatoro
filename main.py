import logging
from os import environ

from discord import AllowedMentions, Intents

from nagatoro.common import Bot, Config


def main():
    config = (
        Config.default()
        .intents(Intents.default())
        .allowed_mentions(AllowedMentions.none())
        .extension_package("nagatoro.extensions")
        .extension(".management")
    )
    bot = Bot(config)

    # Token is stored outside of the config object for security reasons
    token = environ.get("BOT_TOKEN")
    bot.run(token, log_handler=None)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    main()
