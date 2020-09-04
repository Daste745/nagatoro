from time import time
from datetime import timedelta

from discord import Color
from discord.ext.tasks import loop
from discord.ext.commands import (
    Cog,
    Context,
    command,
    group,
    is_owner,
    cooldown,
    BucketType,
)
from pony.orm import db_session

from nagatoro.objects import Embed
from nagatoro.utils.db import get_guild
from nagatoro.checks import is_moderator
from nagatoro.db import Guild


class Management(Cog, command_attrs=dict(ignore_extra=True)):
    """Bot settings and info"""

    def __init__(self, bot):
        self.bot = bot
        self.wake_database.start()

    def cog_unload(self):
        self.wake_database.cancel()

    @command(name="reload", aliases=["r"], hidden=True)
    @is_owner()
    async def reload(self, ctx: Context):
        """Reload all cogs and commands"""

        ctx.bot.reload_cogs()
        await ctx.send(
            f"Reloaded **{len(ctx.bot.commands)}** commands "
            f"from **{len(ctx.bot.cogs)}** modules."
        )

    @command(name="ping")
    async def ping(self, ctx: Context):
        """Shows the bot's ping to the web socket"""

        embed = Embed(ctx, title="Ping")
        ping = round(self.bot.latency * 1000)

        embed.description = f":ping_pong:‎‎{ping}ms"
        await ctx.send(embed=embed)
        return ping

    @command(name="uptime")
    async def uptime(self, ctx: Context):
        """Time from the start of the bot"""

        current_timestamp = time()
        timestamp_difference = round(current_timestamp - self.bot.start_timestamp)
        uptime = timedelta(seconds=timestamp_difference)
        embed = Embed(ctx, title="Uptime", description=str(uptime))

        await ctx.send(embed=embed)
        return uptime

    @group(name="prefix", invoke_without_command=True)
    @cooldown(rate=2, per=10, type=BucketType.user)
    async def prefix(self, ctx: Context):
        """Custom bot prefix"""

        embed = Embed(
            ctx,
            title=f"Prefixes for {ctx.guild.name}",
            description="",
            color=Color.blue(),
        )

        for i in (await ctx.bot.command_prefix(ctx.bot, ctx.message))[1:]:
            embed.description += f"- **{i}**\n"

        return await ctx.send(embed=embed)

    @prefix.command(name="set")
    @is_moderator()
    @cooldown(rate=2, per=30, type=BucketType.guild)
    async def prefix_set(self, ctx: Context, prefix: str):
        """Set a custom prefix for this server"""

        guild = await Guild.get(id=ctx.guild.id)
        guild.prefix = prefix
        await guild.save()

        await ctx.send(f"Set custom prefix to `{prefix}`")

    @prefix.command(name="delete", aliases=["unset", "remove", "del"])
    @is_moderator()
    @cooldown(rate=2, per=30, type=BucketType.guild)
    async def prefix_delete(self, ctx: Context):
        """Delete the prefix from this server"""

        guild = await Guild.get(id=ctx.guild.id)
        if not guild.prefix:
            return await ctx.send(
                f"**{ctx.guild.name}** " f"doesn't have a custom prefix."
            )

        guild.prefix = None
        await guild.save()

        await ctx.send(f"Removed prefix from **{ctx.guild.name}**")

    # This is just a hack to keep the database busy
    # and to not let it block the bot thread after ~20 minutes of inactivity
    # TODO: Use proper async ORM.
    @loop(minutes=10)
    async def wake_database(self):
        with db_session:
            temp = await get_guild(123)
            temp.delete()


def setup(bot):
    bot.add_cog(Management(bot))
