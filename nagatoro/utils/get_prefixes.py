from discord import DMChannel
from discord.ext.commands import when_mentioned_or

from nagatoro.db import Guild


async def get_prefixes(bot, message):
    prefixes = [bot.config.prefix]

    if not bot.config.testing and not isinstance(message.channel, DMChannel):
        guild, _ = await Guild.get_or_create(id=message.guild.id)
        if guild.prefix:
            prefixes.append(guild.prefix)

    return when_mentioned_or(*prefixes)(bot, message)
