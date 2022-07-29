import re
from discord import utils
from discord.ext.commands import Converter, Context
from discord.ext.commands.errors import BadArgument


class User(Converter):
    async def convert(self, ctx: Context, argument: str):
        user_id_match = re.match(r"<@(!|)(?P<id>\d+)>", argument)

        if not user_id_match:
            try:
                member = utils.find(
                    lambda x: x.name.lower() == argument.lower(),
                    ctx.guild.members)
                user_id = member.id
            except:
                user_id = argument
        else:
            user_id = user_id_match.group("id")

        try:
            return await ctx.bot.fetch_user(user_id=user_id)
        except:
            raise BadArgument(f"User {argument} not found.")
