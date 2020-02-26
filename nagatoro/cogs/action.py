import json
from asyncio import TimeoutError
from discord.ext.commands import Cog, Context, command, cooldown, \
    BucketType

from nagatoro.objects import Embed
from nagatoro.utils import get_gif


with open("data/action_config.json", "r") as f:
    action_commands = json.load(f)["commands"]


class Action(Cog):
    """Action and reaction GIFs"""

    def __init__(self, bot):
        self.bot = bot

    @command(name="action", ignore_extra=True, aliases=action_commands)
    @cooldown(rate=3, per=15, type=BucketType.user)
    async def action(self, ctx: Context):
        """Send an action gif"""

        if ctx.invoked_with == "action":
            embed = Embed(ctx, title="Action", footer="Powered By Tenor")
            embed.add_field(name="Available commands",
                            value=", ".join(self.action.aliases))
            return await ctx.send(embed=embed)

        await ctx.trigger_typing()
        embed = Embed(ctx, footer="Via Tenor", color=ctx.author.color)
        embed.set_image(
            url=await get_gif(ctx.invoked_with, self.bot.config.tenor_key))

        message = await ctx.send(embed=embed)

        await message.add_reaction("🔁")

        while True:
            try:
                await self.bot.wait_for(
                    "reaction_add",
                    timeout=20,
                    check=lambda r, u: u == ctx.message.author
                                       and str(r.emoji) == "🔁")

                embed.set_image(
                    url=await get_gif(ctx.invoked_with,
                                      self.bot.config.tenor_key))
                await message.edit(embed=embed)
            except TimeoutError:
                await message.clear_reactions()
                break


def setup(bot):
    bot.add_cog(Action(bot))
