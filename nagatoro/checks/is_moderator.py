from pony.orm import db_session
from discord import utils
from discord.ext.commands import Context, check
from discord.ext.commands.errors import MissingRole, CommandError

from nagatoro.utils.db import get_guild, get_mod_role


def is_moderator():
    async def predicate(ctx: Context):
        with db_session:
            guild = await get_guild(ctx.guild.id)

            if guild.mod_role not in [i.id for i in ctx.author.roles] \
                    or not guild.mod_role:
                mod_role = await get_mod_role(ctx.bot, ctx.guild.id)

                if not mod_role:
                    raise CommandError("Mod role was not set for this server.")
                else:
                    raise MissingRole(mod_role.name)
            else:
                return True

    return check(predicate)
