from discord import utils
from discord.ext.commands import Context, Converter
from discord.ext.commands.errors import BadArgument


class Role(Converter):
    async def convert(self, ctx: Context, argument: str):
        role = utils.find(
            lambda x: x.name.lower() == argument.lower(),
            ctx.guild.roles)

        if not role:
            raise BadArgument(f"Role {argument} not found.")

        return role
