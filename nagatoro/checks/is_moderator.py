from discord.ext.commands import Context, check
from discord.ext.commands.errors import MissingRole, CommandError

from nagatoro.db import Guild


def is_moderator():
    async def predicate(ctx: Context):
        guild, _ = await Guild.get_or_create(id=ctx.guild.id)

        if guild.moderator_role not in [i.id for i in ctx.author.roles]:
            moderator_role = ctx.guild.get_role(guild.moderator_role)

            if not moderator_role:
                raise CommandError("Mod role was not set for this server.")
            else:
                raise MissingRole(moderator_role.name)
        else:
            return True

    return check(predicate)
