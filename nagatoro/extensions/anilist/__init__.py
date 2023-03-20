from nagatoro.common import Bot

from .cogs import AniList


async def setup(bot: Bot) -> None:
    await bot.add_cog(AniList(bot))
