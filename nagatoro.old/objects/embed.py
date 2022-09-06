from typing import Tuple
import discord
from discord.ext.commands import Context


class Embed(discord.Embed):
    def __init__(self, ctx: Context, *, footer: str = None, **kwargs):
        super(Embed, self).__init__(**kwargs)
        self.timestamp = ctx.message.created_at

        footer_content = [str(ctx.author)]
        if footer:
            footer_content.append(footer)
        self.set_footer(
            text=" | ".join(footer_content), icon_url=ctx.author.avatar_url)

    def add_fields(self, *fields: Tuple[str, str]):
        for name, value in fields:
            self.add_field(name=name, value=value)
