import discord
from discord import Guild
from discord.ext import commands
from discord.ext.commands import Context, Greedy

from nagatoro.common import Bot, Cog


@commands.is_owner()
class Management(Cog):
    @commands.command(name="reload", aliases=["r"])
    async def reload(self, ctx: Context):
        """Reload all loaded extensions"""

        async with ctx.typing():
            await self.bot.reload_extensions()

            await ctx.send("Reloaded extensions")

    @commands.group(name="sync", invoke_without_command=True)
    @commands.guild_only()
    async def sync(self, ctx: Context):
        """Sync global commands to the current guild"""

        async with ctx.typing():
            self.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await self.bot.tree.sync(guild=ctx.guild)

            await ctx.send(f"Synced {len(synced)} command(s) to this guild")

    @sync.command(name="global")
    async def sync_global(self, ctx: Context):
        """Sync global commands"""

        async with ctx.typing():
            synced = await self.bot.tree.sync()

            await ctx.send(f"Synced {len(synced)} command(s) globally")

    @sync.command(name="guild", aliases=["guilds"])
    @commands.guild_only()
    async def sync_guild(self, ctx: Context, guilds: Greedy[Guild] = None):
        """Sync guild commands"""

        if not guilds:
            guilds = [ctx.guild]

        guild_count = 0
        command_count = 0

        async with ctx.typing():
            for guild in guilds:
                try:
                    synced = await self.bot.tree.sync(guild=guild)
                    guild_count += 1
                    command_count += len(synced)
                except discord.HTTPException:
                    pass

            await ctx.send(
                f"Synced {command_count} command(s) to {guild_count} guild(s)"
            )

    @commands.command(name="clear")
    @commands.guild_only()
    async def clear(self, ctx: Context, guilds: Greedy[Guild] = None):
        """Clear commands from guilds"""

        if not guilds:
            guilds = [ctx.guild]

        guild_count = 0

        async with ctx.typing():
            for guild in guilds:
                try:
                    self.bot.tree.clear_commands(guild=guild)
                    await self.bot.tree.sync(guild=guild)
                    guild_count += 1
                except discord.HTTPException:
                    pass

            await ctx.send(f"Cleared commands from {guild_count} guild(s)")

    @commands.command(name="rs")
    async def reload_and_sync(self, ctx: Context, clear: bool = False):
        """Reload all loaded extensions and sync global commands to the current guild"""

        await self.reload(ctx)
        await self.sync(ctx, clear)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Management(bot))
