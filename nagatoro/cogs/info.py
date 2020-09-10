from time import time
from datetime import timedelta

from discord.ext.commands import Cog, Context, command

from nagatoro.objects import Embed


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

        ping = round(self.bot.latency * 1000)
        embed = Embed(ctx, title="Ping", description=f":ping_pong:‎‎{ping}ms")

        await ctx.send(embed=embed)

    @command(name="uptime")
    async def uptime(self, ctx: Context):
        """Bot uptime"""

        current_timestamp = time()
        timestamp_difference = round(current_timestamp - self.bot.start_timestamp)
        uptime = timedelta(seconds=timestamp_difference)
        embed = Embed(ctx, title="Uptime", description=str(uptime))

        await ctx.send(embed=embed)

    @command(name="support")
    async def support(self, ctx: Context):
        """Invite to Nagatoro's support server"""

        await ctx.send("Sent you an invite, check your DMs")
        await ctx.author.send("https://discord.gg/qDzU7gd")

    @command(name="bug")
    async def bug(self, ctx: Context):
        """Where to report bugs and feature requests"""

        embed = Embed(
            ctx,
            title="Bug reporting",
            description="You can report bugs directly to me (@Predator#xxxx) "
            "or preferrably, if you are familiar with GitHub, on the "
            "[issues page](https://github.com/stefankar1000/nagatoro/issues)"
            "\n\nPlease, provide any errors and context while reporting bugs "
            "and clearly explain the issue.",
        )

        await ctx.send(embed=embed)

    @command(name="invite")
    async def invite(self, ctx: Context):
        """Nagatoro's bot invite link"""

        invite = (
            "https://discord.com/oauth2/authorize"
            "?client_id=672485626179747864&scope=bot&permissions=268443716"
        )

        embed = Embed(
            ctx,
            title="Nagatoro invite link",
            url=invite,
            description=(
                "Nagatoro requires permissions for some commands to work:\n"
                "**Manage Roles** - Used by the Moderation module for muting\n"
                "**Ban Members** - Used only by the ban command, can be left off\n"
                "**Manage Messages** - Automatic reaction removal while refreshing\n"
                "**Add Reactions** - Confirmations and reloading gifs\n\n"
                "If any permissions are missing, an appropriate message will "
                "be displayed, these can be turned on or off at any time in "
                "server settings."
            ),
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
