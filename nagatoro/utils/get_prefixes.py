from discord.ext.commands import when_mentioned_or, when_mentioned

from nagatoro.db import Guild


async def get_prefixes(bot, message):
    prefixes = []

    if prefix := bot.config.prefix:
        prefixes.append(prefix)

    if message.guild:
        guild, _ = await Guild.get_or_create(id=message.guild.id)
        if guild.prefix:
            prefixes.append(guild.prefix)

    if prefixes:
        return when_mentioned_or(*prefixes)(bot, message)
    else:
        return when_mentioned(bot, message)
