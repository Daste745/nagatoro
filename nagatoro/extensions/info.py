from datetime import datetime

from discord import Interaction, app_commands
from discord.ext import commands
from discord.ext.commands import Context

from nagatoro.common import Bot, Cog


class Info(Cog):
    @app_commands.command()
    async def ping(self, itx: Interaction):
        """Ping the bot"""

        latency_ms = round(self.bot.latency * 1000)
        await itx.response.send_message(
            f"Pong! :ping_pong: \n\nWebsocket latency: {latency_ms}ms"
        )


@commands.is_owner()
class AdminInfo(Cog):
    @commands.command(name="uptime")
    async def uptime(self, ctx: Context):
        """Check the bot's uptime"""

        now = datetime.utcnow()
        delta = now - self.bot.start_timestamp

        await ctx.send(f"Bot uptime: {delta}")


async def setup(bot: Bot) -> None:
    await bot.add_cog(Info(bot))
    await bot.add_cog(AdminInfo(bot))
