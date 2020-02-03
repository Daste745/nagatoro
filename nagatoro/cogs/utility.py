from typing import Union
from discord import Color
from discord.ext.commands import Cog, Context, command

from nagatoro.converters import Role, User, Member
from nagatoro.objects import Embed


class Utility(Cog):
    """Utility commands"""
    def __init__(self, bot):
        self.bot = bot

    @command(name="role")
    async def role(self, ctx: Context, *, role: Role):
        """Shows info about a role"""
        embed = Embed(ctx, title=role.name, color=role.color)

        embed.add_field(name="ID", value=role.id)

        if len(role.members) > 1:
            embed.add_field(name="Members", value=str(len(role.members)))

        embed.add_field(name="Mentionable",
                        value="Yes" if role.mentionable else "No")

        if role.color != Color.default():
            embed.add_field(name="Color",
                            value=f"{role.color}, rgb{role.color.to_rgb()}")

        embed.add_field(name="Created at", value=role.created_at)

        await ctx.send(embed=embed)

    @command(name="user", aliases=["me", "member"])
    async def user(self, ctx: Context, *, user: Union[Member, User] = None):
        """Shows info about an user or a member"""
        if not user:
            user = ctx.author

        title = str(user) if not user.bot else f"{user} :robot:"
        embed = Embed(ctx, title=title, color=user.color)
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="ID", value=user.id, inline=False)
        embed.add_field(name="Created at", value=user.created_at)

        await ctx.send(embed=embed)

    @command(name="avatar", aliases=["av", "pfp"])
    async def avatar(self, ctx: Context, *, user: User = None):
        """Shows an user's avatar"""
        if not user:
            user = ctx.author

        embed = Embed(ctx, title=f"{user.name}'s avatar")
        embed.set_image(url=user.avatar_url_as(size=2048))
        await ctx.send(embed=embed)

    @command(name="server", aliases=["guild"])
    async def server(self, ctx: Context):
        """Shows info about this server"""
        embed = Embed(ctx, title=ctx.guild.name)
        embed.set_thumbnail(url=ctx.guild.icon_url_as(size=2048))
        embed.add_field(name="ID", value=ctx.guild.id)
        embed.add_field(name="Owner", value=ctx.guild.owner.mention)
        embed.add_field(name="Region", value=ctx.guild.region)
        embed.add_field(name="Members", value=str(ctx.guild.member_count))
        embed.add_field(name="Text channels",
                        value=str(len(ctx.guild.text_channels)))
        embed.add_field(name="Voice channels",
                        value=str(len(ctx.guild.voice_channels)))
        embed.add_field(name="Emojis",
                        value=" ".join([str(i) for i in ctx.guild.emojis]))

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
