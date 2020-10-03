from asyncio import TimeoutError
from discord.errors import Forbidden
from discord.ext.commands import Cog, Context, command, cooldown, BucketType

from nagatoro.objects import Embed
from nagatoro.utils import get_gif


available_commands = [
    "hug",
    "pat",
    "smile",
    "cuddle",
    "snuggle",
    "kiss",
    "pout",
    "slap",
    "bite",
    "lick",
    "tickle",
    "poke",
    "meow",
    "goodnight",
]

action_description = """
        Pressing the 🔁 reaction reloads the image for a new one.
        The option to refresh lasts 30 seconds and only you can use it.
        """


class Action(Cog):
    """Action and reaction GIFs"""

    def __init__(self, bot):
        self.bot = bot

        commands = []
        # Create all action commands
        for name in available_commands:
            desciption = f"Send a '{name}' gif from Tenor\n{action_description}"
            cmd = self.action.copy()
            cmd.update(name=name, help=desciption, cog=self)
            commands.append(cmd)

        self.__cog_commands__ = tuple(commands)

    @command(name="action", ignore_extra=True)
    @cooldown(rate=3, per=15, type=BucketType.user)
    async def action(self, ctx: Context):
        """Send an action gif

        Pressing the 🔁 reaction reloads the image for a new one.
        The option to refresh lasts 30 seconds and only you can use it.
        """

        await ctx.trigger_typing()
        embed = Embed(ctx, footer="Via Tenor", color=ctx.author.color)
        embed.set_image(url=await get_gif(ctx.invoked_with, self.bot.config.tenor_key))

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
    if not bot.config.tenor_key:
        return

    bot.add_cog(Action(bot))
