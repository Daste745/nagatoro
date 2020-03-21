from discord.ext import commands
from discord import Message, DMChannel

from nagatoro.utils.db import get_prefix


async def get_prefixes(bot: commands.Bot, message: Message):
    prefixes = [bot.config.prefix]
    # TODO: Make prefix caching, so we don't constantly use the database.
    if not isinstance(message.channel, DMChannel) \
            and not bot.config.testing \
            and (prefix := await get_prefix(message.guild.id)):
        # 'not bot.config.testing' prevents double messages when running
        # a development instance of the bot.
        prefixes.append(prefix)

    return commands.when_mentioned_or(*prefixes)(bot, message)
