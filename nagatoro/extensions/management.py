import discord
from discord import Guild
from discord.ext import commands
from discord.ext.commands import Context, Greedy

from nagatoro.common import Bot, Cog


class Management(Cog):
    @commands.command(name="reload", aliases=["r"])
    async def reload(self, ctx: Context):
        async with ctx.typing():
            await self.bot.reload_extensions()

            await ctx.send("Reloaded extensions.")

    @commands.group(name="sync")
    async def sync(self, ctx: Context):
        await self.sync_global(ctx)

    @sync.command(name="global")
    async def sync_global(self, ctx: Context):
        """Sync all commands globally"""

        async with ctx.typing():
            synced = await self.bot.tree.sync()

            await ctx.send(content=f"Synced {len(synced)} command(s) globally")

    @sync.command(name="guild", aliases=["guilds"])
    async def sync_guild(self, ctx: Context, guilds: Greedy[Guild] = None):
        """Sync commands to given guild(s)"""

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
                content=f"Synced {command_count} command(s) to {guild_count} guild(s)"
            )


async def setup(bot: Bot) -> None:
    await bot.add_cog(Management(bot))
