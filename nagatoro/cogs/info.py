from time import time
from datetime import timedelta

from discord.ext.commands import Cog, Context, command

from nagatoro.objects import Embed
from nagatoro.utils import t


class Info(Cog):
    """Info about Nagatoro"""

    def __init__(self, bot):
        self.bot = bot
        # NOTE: This could be unsafe
        bot.help_command.cog = self

    @command(name="ping")
    async def ping(self, ctx: Context):
        """Bot connection latency

        This isn't very accurate, and mainly used as a "is this bot alive?" command.
        """

        embed = Embed(
            ctx,
            title=t(ctx, "title"),
            description=t(ctx, "message", ping=round(self.bot.latency * 1000)),
        )

        await ctx.send(embed=embed)

    @command(name="uptime")
    async def uptime(self, ctx: Context):
        """Bot uptime"""

        timestamp_difference = round(time() - self.bot.start_timestamp)
        uptime = timedelta(seconds=timestamp_difference)
        embed = Embed(ctx, title=t(ctx, "title"), description=str(uptime))

        await ctx.send(embed=embed)

    @command(name="support")
    async def support(self, ctx: Context):
        """Invite to Nagatoro's support server"""

        await ctx.send(t(ctx, "message"))
        await ctx.author.send(t(ctx, "invite_url"))

    @command(name="bug")
    async def bug(self, ctx: Context):
        """Where to report bugs and feature requests"""

        embed = Embed(
            ctx,
            title=t(ctx, "title"),
            description=t(ctx, "message"),
        )

        await ctx.send(embed=embed)

    @command(name="invite")
    async def invite(self, ctx: Context):
        """Nagatoro's bot invite link"""

        embed = Embed(
            ctx,
            title=t(ctx, "title"),
            url=t(ctx, "invite_url"),
            description=t(ctx, "message"),
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
