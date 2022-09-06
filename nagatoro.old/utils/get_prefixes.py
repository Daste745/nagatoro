from typing import Optional

from discord.ext.commands import when_mentioned_or, when_mentioned


async def get_prefixes(bot, message):
    prefix: Optional[str] = bot.config.prefix

    cache_key = f"{message.guild.id}:prefix"
    if bot.cache.exists(cache_key):
        prefix = bot.cache.get(cache_key).decode()

    if prefix:
        return when_mentioned_or(prefix)(bot, message)
    else:
        return when_mentioned(bot, message)
