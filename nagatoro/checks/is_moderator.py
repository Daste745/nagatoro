from discord.ext.commands import Context, check
from discord.ext.commands.errors import CheckFailure

from nagatoro.db import Moderator


class NotModerator(CheckFailure):
    """Exception raised when the command invoker isn't on the moderator list."""

    def __init__(self):
        super().__init__(
            "You are not a moderator on this server. See the `moderators` command."
        )


def is_moderator():
    async def predicate(ctx: Context):
        moderator = await Moderator.get_or_none(
            user__id=ctx.author.id, guild__id=ctx.guild.id
        )
        if not moderator:
            raise NotModerator()
        else:
            return True

    return check(predicate)
