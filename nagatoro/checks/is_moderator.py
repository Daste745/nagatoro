from discord.ext.commands import Context, check
from discord.ext.commands.errors import CheckFailure


class NotModerator(CheckFailure):
    """Exception raised when the command invoker isn't on the moderator list."""

    def __init__(self):
        super().__init__(
            "You are not a moderator on this server. See the `moderators` command."
        )


def is_moderator():
    async def predicate(ctx: Context):
        if not ctx.bot.cache.sismember(
            f"{ctx.guild.id}:moderators",
            ctx.author.id,
        ):
            raise NotModerator()
        return True

    return check(predicate)
