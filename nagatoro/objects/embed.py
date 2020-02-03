import discord
from discord.ext.commands import Context


class Embed(discord.Embed):
    def __init__(self, ctx: Context, **kwargs):
        super(Embed, self).__init__(**kwargs)
        self.timestamp = ctx.message.created_at
        self.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
