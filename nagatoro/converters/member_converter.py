import re
from discord import utils
from discord.ext.commands import Context, Converter
from discord.ext.commands.errors import BadArgument


class Member(Converter):
    async def convert(self, ctx: Context, argument: str):
        member_id_match = re.match(r"(<@)?(!|)(?P<id>\d+)>?", argument)

        if not member_id_match:
            member = utils.find(
                lambda x: x.name.lower() == argument.lower(),
                ctx.guild.members)
        else:
            print(member_id_match.group("id"))
            member = utils.find(
                lambda x: x.id == int(member_id_match.group("id")),
                ctx.guild.members)

        if not member:
            raise BadArgument(f"Member {argument} not found.")

        return member
