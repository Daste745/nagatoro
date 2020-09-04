from discord import Message, DMChannel
from discord.ext.commands import when_mentioned_or

from nagatoro.utils.db import get_prefix


async def get_prefixes(bot, message: Message):
    prefixes = [bot.config.prefix]
    if (
        not isinstance(message.channel, DMChannel)
        and not bot.config.testing
        and (prefix := await get_prefix(message.guild.id))
    ):
        # 'not bot.config.testing' prevents double messages when running
        # a development instance of the bot.
        prefixes.append(prefix)

    return when_mentioned_or(*prefixes)(bot, message)
