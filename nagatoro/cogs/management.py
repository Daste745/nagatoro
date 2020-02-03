import os
from time import time
from datetime import timedelta
from pony.orm import db_session
from discord import Color
from discord.ext.commands import Cog, Context, Bot, command, group, is_owner
from discord.ext.commands.errors import NotOwner

from nagatoro.objects.database import Guild
from nagatoro.objects import Embed


class Management(Cog, command_attrs=dict(ignore_extra=True)):
    """Commands to manage the bot's settings"""
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def load_cogs(bot: Bot):
        path = "nagatoro/cogs/"
        extensions = [path.replace("/", ".") + i.replace(".py", "")
                      for i in os.listdir(path)
                      if os.path.isfile(f"{path}{i}")]
        for extension in extensions:
            bot.load_extension(extension)

    @staticmethod
    def unload_cogs(bot: Bot):
        for extension in list(bot.extensions):
            bot.unload_extension(extension)

    @command(name="reload", aliases=["r"], hidden=True)
    @is_owner()
    async def reload(self, ctx: Context):
        self.unload_cogs(self.bot)
        self.load_cogs(self.bot)
        await ctx.send(f"Reloaded **{len(self.bot.commands)}** commands.")

    @command(name="ping")
    async def ping(self, ctx: Context):
        """Shows the bot's ping to the web socket"""
        embed = Embed(ctx, title="Ping")
        ping = round(self.bot.latency * 1000)
        embed.description = f":ping_pong:‎‎{ping}ms"
        await ctx.send(embed=embed)

    @command(name="uptime")
    async def uptime(self, ctx: Context):
        current_timestamp = time()
        timestamp_difference = round(current_timestamp -
                                     self.bot.start_timestamp)
        uptime = timedelta(seconds=timestamp_difference)
        embed = Embed(ctx, title="Uptime", description=str(uptime))

        await ctx.send(embed=embed)

    @group(name="prefix")
    async def prefix(self, ctx: Context):
        """Shows the current prefix"""
        if ctx.invoked_subcommand:
            return

        with db_session:
            if not Guild.get(id=ctx.guild.id):
                Guild(id=ctx.guild.id)
            guild = Guild.get(id=ctx.guild.id)

            if not guild.prefix:
                prefix = ctx.prefix
            else:
                prefix = guild.prefix
            embed = Embed(ctx, title="Prefix", color=Color.blue())
            embed.description = f"The current prefix is `{prefix}`"
            await ctx.send(embed=embed)

    @prefix.command(name="set")
    async def prefix_set(self, ctx: Context, prefix: str):
        """Shows the prefix for this server"""
        if ctx.author != ctx.guild.owner:
            raise NotOwner("You are not the owner of this guild!")

        with db_session:
            if not Guild.get(id=ctx.guild.id):
                Guild(id=ctx.guild.id)
            guild = Guild.get(id=ctx.guild.id)

            guild.prefix = prefix
            await ctx.send(f"Set custom prefix to `{guild.prefix}`")

    @prefix.command("remove", aliases=["unset"])
    async def prefix_remove(self, ctx: Context):
        """Removes the prefix for this server"""
        if ctx.author != ctx.guild.owner:
            raise NotOwner("You are not the owner of this guild!")

        with db_session:
            if not Guild.get(id=ctx.guild.id):
                Guild(id=ctx.guild.id)
            guild = Guild.get(id=ctx.guild.id)

            if not guild.prefix:
                await ctx.send("This guild doesn't have a prefix.")
            else:
                await ctx.send(f"Removed prefix `{guild.prefix}`")
                guild.prefix = None


def setup(bot):
    bot.add_cog(Management(bot))
