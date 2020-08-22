import json
from asyncio import TimeoutError
from discord.errors import Forbidden
from discord.ext.commands import Cog, Context, command, cooldown, BucketType

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

        if not ctx.channel.permissions_for(ctx.me).add_reactions:
            # Do not create the refresh loop if bot can't add reactions
            return

        refresh_emoji = "🔁"
        await message.add_reaction(refresh_emoji)

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == refresh_emoji

        while True:
            try:
                await self.bot.wait_for("reaction_add", timeout=30, check=check)

                embed.set_image(
                    url=await get_gif(ctx.invoked_with, self.bot.config.tenor_key)
                )
                await message.edit(embed=embed)

                try:
                    await message.remove_reaction(refresh_emoji, ctx.author)
                except Forbidden:
                    # No manage_messages permission
                    pass
            except TimeoutError:
                await message.clear_reactions()
                break


def setup(bot):
    bot.add_cog(Action(bot))
