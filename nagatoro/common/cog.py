from discord.ext import commands

from .bot import Bot


class Cog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot


class GroupCog(commands.GroupCog, metaclass=commands.CogMeta):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        super().__init__()
