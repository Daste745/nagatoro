from discord.ext.commands import when_mentioned_or, when_mentioned

from nagatoro.db import Guild


async def get_prefixes(bot, message):
    guild, _ = await Guild.get_or_create(id=message.guild.id)

    if bot.config.prefix or (guild and guild.prefix):
        return when_mentioned_or(guild.prefix or bot.config.prefix)(bot, message)
    else:
        return when_mentioned(bot, message)
