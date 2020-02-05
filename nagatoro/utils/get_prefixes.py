from discord.ext import commands
from discord import Message

from nagatoro.utils.db import get_prefix


async def get_prefixes(bot: commands.Bot, message: Message):
    prefixes = [";"]
    if prefix := await get_prefix(message.guild.id):
        prefixes.append(prefix)

    return commands.when_mentioned_or(*prefixes)(bot, message)
