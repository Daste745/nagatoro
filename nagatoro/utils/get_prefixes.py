from pony.orm import db_session
from discord.ext import commands
from discord import Message

from nagatoro.objects.database import Guild


async def get_prefixes(bot: commands.Bot, message: Message):
    prefixes = [";"]
    with db_session:
        if (guild := Guild.get(id=message.guild.id)) and guild.prefix:
            prefixes.append(guild.prefix)

    return commands.when_mentioned_or(*prefixes)(bot, message)
