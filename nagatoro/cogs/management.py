from discord import Color, TextChannel
from discord.ext.commands import (
    Cog,
    Context,
    command,
    group,
    is_owner,
    cooldown,
    BucketType,
)

from nagatoro.objects import Embed
from nagatoro.checks import is_moderator
from nagatoro.db import Guild


class Management(Cog, command_attrs=dict(ignore_extra=True)):
    """Bot settings and info"""

    def __init__(self, bot):
        self.bot = bot

    @command(name="reload", aliases=["r"], hidden=True)
    @is_owner()
    async def reload(self, ctx: Context):
        """Reload all cogs and commands"""

        ctx.bot.reload_cogs()
        await ctx.send(
            f"Reloaded **{len(ctx.bot.commands)}** commands "
            f"from **{len(ctx.bot.cogs)}** modules."
        )

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

    @command(name="disable_channel")
    @is_moderator()
    @cooldown(rate=2, per=10, type=BucketType.user)
    async def disable_channel(self, ctx: Context, channel: TextChannel):
        """Disable channel from bot reacting"""

        g, _ = await Guild.get_or_create(id=ctx.guild.id)
        status = f"Enable <#{channel.id}>"

        if channel.id in g.disabled_channels:
            g.disabled_channels.remove(channel.id)
        else:
            g.disabled_channels.append(channel.id)
            status = f"Disabled <#{channel.id}>"

        await g.save()
        return await ctx.send(status)


def setup(bot):
    bot.add_cog(Management(bot))
