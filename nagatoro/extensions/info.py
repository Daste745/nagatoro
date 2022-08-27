from datetime import datetime

from discord import Interaction, app_commands

from nagatoro.common import Bot, Cog


class Info(Cog):
    @app_commands.command()
    async def ping(self, itx: Interaction):
        """Ping the bot"""

        latency_ms = round(self.bot.latency * 1000)
        await itx.response.send_message(
            f"Pong! :ping_pong: \n\nWebsocket latency: {latency_ms}ms"
        )

    @app_commands.command()
    async def uptime(self, itx: Interaction):
        """Check the bot's uptime"""

        now = datetime.utcnow()
        delta = now - self.bot.start_timestamp

        await itx.response.send_message(f"Bot uptime: {delta}")


async def setup(bot: Bot) -> None:
    await bot.add_cog(Info(bot))
