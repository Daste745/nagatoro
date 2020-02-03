from discord.ext.commands import Context, check


def is_server_owner():
    async def predicate(ctx: Context):
        print(ctx.author, ctx.guild.owner)
        return ctx.author == ctx.guild.owner

    return check(predicate)
