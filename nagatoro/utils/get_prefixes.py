from discord.ext import commands
from discord import Message

from nagatoro.utils.db import get_prefix


async def get_prefixes(bot: commands.Bot, message: Message):
    prefixes = [bot.config.prefix]
    # TODO: Make prefix caching, so we don't constantly use the database.
    if prefix := await get_prefix(message.guild.id):
        prefixes.append(prefix)

    return commands.when_mentioned_or(*prefixes)(bot, message)
