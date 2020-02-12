import os
import platform
from psutil import virtual_memory
from cpuinfo import get_cpu_info
from time import time
from discord import __version__ as discord_version
from datetime import timedelta
from discord import Color
from discord.ext.commands import Cog, Context, Bot, command, group, is_owner, \
    ExtensionAlreadyLoaded
from discord.ext.tasks import loop

from nagatoro.objects import Embed
from nagatoro.utils.db import get_prefix, set_prefix


def get_size(bytes: int):
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}"
        bytes /= 1024


class Management(Cog, command_attrs=dict(ignore_extra=True)):
    """Commands to manage the bot's settings"""
    def __init__(self, bot):
        self.bot = bot
        self.wake_database.start()

    def cog_unload(self):
        self.wake_database.cancel()

    @staticmethod
    def load_cogs(bot: Bot):
        path = "nagatoro/cogs/"
        extensions = [path.replace("/", ".") + i.replace(".py", "")
                      for i in os.listdir(path)
                      if os.path.isfile(f"{path}{i}")]
        for extension in extensions:
            try:
                bot.load_extension(extension)
            except ExtensionAlreadyLoaded:
                pass

    @command(name="reload", aliases=["r"], hidden=True)
    @is_owner()
    async def reload(self, ctx: Context):
        """Reload all cogs and commands"""

        for extension in list(self.bot.extensions):
            try:
                self.bot.reload_extension(extension)
            except ExtensionAlreadyLoaded:
                pass

        await ctx.send(f"Reloaded **{len(self.bot.commands)}** commands.")

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
        timestamp_difference = round(current_timestamp -
                                     self.bot.start_timestamp)
        uptime = timedelta(seconds=timestamp_difference)
        embed = Embed(ctx, title="Uptime", description=str(uptime))

        await ctx.send(embed=embed)
        return uptime

    @command(name="info")
    async def info(self, ctx: Context):
        """Bot info"""
        git_branch = os.popen(
            "git branch | awk '{print $2}' | sed '/^\s*$/d'").read()

        embed = Embed(ctx, title="Bot info", color=Color(0x56517b))
        if self.bot.config.testing:
            embed.description = f"Development version, git: **{git_branch}**"
        embed.set_thumbnail(url=self.bot.user.avatar_url)

        embed.add_fields(
            ("Ping", f"{round(self.bot.latency * 1000)}ms"),
            ("Uptime",
             str(timedelta(seconds=round(time() - self.bot.start_timestamp)))),
            ("Commands", f"{len(self.bot.commands)} commands"),
            ("Creator", str(await self.bot.fetch_user(self.bot.owner_id))),
            ("Library", f"discord.py {discord_version}"),
            ("Python version",
             f"{platform.python_implementation()} {platform.python_version()}"),
            ("System", f"{platform.system()} {platform.release()}"),
            ("Processor", get_cpu_info()["brand"]),
            ("Memory",
             f"{get_size(virtual_memory().used)}/"
             f"{get_size(virtual_memory().total)} "
             f"({virtual_memory().percent}%)")
        )

        await ctx.send(embed=embed)

    @group(name="prefix")
    async def prefix(self, ctx: Context):
        """Shows the current prefix"""

        if ctx.invoked_subcommand:
            return

        if not (prefix := await get_prefix(ctx.guild.id)):
            prefix = ctx.prefix

        embed = Embed(ctx, title="Prefix", color=Color.blue())
        embed.description = f"The current prefix is `{prefix}`"
        return await ctx.send(embed=embed)

    @prefix.command(name="set")
    @is_owner()
    async def prefix_set(self, ctx: Context, prefix: str):
        """Shows the prefix for this server"""

        await set_prefix(ctx.guild.id, prefix)
        return await ctx.send(f"Set custom prefix to `{prefix}`")

    @prefix.command("remove", aliases=["unset", "delete"])
    @is_owner()
    async def prefix_remove(self, ctx: Context):
        """Removes the prefix for this server"""

        await set_prefix(ctx.guild.id, None)
        await ctx.send(f"Removed prefix from **{ctx.guild.name}**")

    # This is just a hack to keep the database busy
    # and to not let it block the bot thread after ~20 minutes of inactivity
    # TODO: Use proper async ORM
    @loop(minutes=10)
    async def wake_database(self):
        if not await get_prefix(123):
            return
        else:
            return


def setup(bot):
    bot.add_cog(Management(bot))
