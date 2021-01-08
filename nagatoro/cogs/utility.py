from typing import Union

from discord import Color
from discord.ext.commands import Cog, Context, command

from nagatoro.converters import Role, User, Member
from nagatoro.objects import Embed
from nagatoro.utils import t


class Utility(Cog):
    """Utility commands"""

    def __init__(self, bot):
        self.bot = bot

    @command(name="role")
    async def role(self, ctx: Context, *, role: Role):
        """Shows info about a role"""

        embed = Embed(ctx, title=t(ctx, "title", role=role.name), color=role.color)

        embed.add_field(name=t(ctx, "id"), value=role.id)

        if len(role.members) > 1:
            embed.add_field(name=t(ctx, "members"), value=str(len(role.members)))

        embed.add_field(
            name=t(ctx, "mentionable"),
            value=t(ctx, "mentionable_yes")
            if role.mentionable
            else t(ctx, "mentionable_no"),
        )

        if role.color != Color.default():
            embed.add_field(
                name=t(ctx, "color"),
                value=t(
                    ctx,
                    "color_value",
                    hex={role.color.value},
                    rgb=role.color.to_rgb(),
                ),
            )

        embed.add_field(name=t(ctx, "created_at"), value=role.created_at)

        await ctx.send(embed=embed)

    @command(name="user", aliases=["me", "member"])
    async def user(self, ctx: Context, *, user: Union[Member, User] = None):
        """Shows info about an user or a member"""

        if not user:
            user = ctx.author

        title = str(user) if not user.bot else t(ctx, "title_bot", user=user.name)
        embed = Embed(ctx, title=title, color=user.color)
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_fields(
            (t(ctx, "id"), user.id),
            (t(ctx, "created_at"), user.created_at),
        )

        await ctx.send(embed=embed)

    @command(name="avatar", aliases=["av", "pfp"])
    async def avatar(self, ctx: Context, *, user: User = None):
        """Shows an user's avatar"""

        if not user:
            user = ctx.author

        embed = Embed(ctx, title=t(ctx, "title", user=user.name))
        embed.set_image(url=user.avatar_url_as(size=2048))
        await ctx.send(embed=embed)

    @command(name="server", aliases=["guild"])
    async def server(self, ctx: Context):
        """Shows info about this server"""

        embed = Embed(ctx, title=ctx.guild.name)
        embed.set_thumbnail(url=ctx.guild.icon_url_as(size=2048))

        embed.add_fields(
            (t(ctx, "id"), ctx.guild.id),
            (t(ctx, "owner"), ctx.guild.owner.mention),
            (t(ctx, "region"), ctx.guild.region),
            (t(ctx, "members"), str(ctx.guild.member_count)),
            (t(ctx, "text_channels"), str(len(ctx.guild.text_channels))),
            (t(ctx, "voice_channels"), str(len(ctx.guild.voice_channels))),
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
