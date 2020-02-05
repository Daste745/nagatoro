from math import sqrt, floor
from pony.orm import db_session, select
from discord import Message, Color
from discord.ext.commands import Cog, Context, command, cooldown, BucketType

import nagatoro.objects.database as db
from nagatoro.converters import Member
from nagatoro.objects import Embed


async def get_profile(user_id: int):
    with db_session:
        if not (user := db.User.get(id=user_id)):
            user = db.User(id=user_id)
        if not (profile := db.Profile.get(user=user)):
            profile = db.Profile(user=user, exp=0, level=0, balance=0)

    return profile


class Profile(Cog):
    """Profile commands"""
    def __init__(self, bot):
        self.bot = bot

    @command(name="profile")
    @cooldown(rate=2, per=10, type=BucketType.user)
    async def profile(self, ctx: Context, *, member: Member = None):
        """User's profile"""

        if not member:
            member = ctx.author

        with db_session:
            profile = await get_profile(member.id)
            progress = round(
                profile.exp / (((profile.level + 1) * 4) ** 2) * 100)

            embed = Embed(
                ctx, title=f"{member.name}'s profile", color=member.color)
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="Level",
                            value=f"{profile.level} ({progress}%)")
            embed.add_field(name="Experience", value=f"{profile.exp} exp")
            embed.add_field(name="Balance", value=f"{profile.balance} coins")
            mutes = select(i for i in profile.user.punishments
                           if isinstance(i, db.Mute)).without_distinct()
            warns = select(i for i in profile.user.punishments
                           if isinstance(i, db.Warn)).without_distinct()
            embed.add_field(name="Mutes", value=str(len(mutes)))
            embed.add_field(name="Warns", value=str(len(warns)))

            await ctx.send(embed=embed)

    @command(name="levels")
    async def levels(self, ctx: Context):
        """Requirements for the next 5 levels"""

        with db_session:
            profile = await get_profile(ctx.author.id)
            embed = Embed(ctx, title="Next 5 levels", description="",
                          color=Color.blue())
            for i in range(profile.level + 1, profile.level + 6):
                embed.description += \
                    f"**Level {i}**: {(i * 4) ** 2} exp\n"

            await ctx.send(embed=embed)

    # TODO: Make exp and balance ranking
    @command(name="ranking", aliases=["top"])
    async def ranking(self, ctx: Context):
        """Top users by level"""

        with db_session:
            top_users = db.Profile.select().order_by(db.desc(db.Profile.exp))[:10]

            embed = Embed(ctx, title="Ranking", description="",
                          color=Color.blue())
            for profile in top_users:
                user = str(self.bot.get_user(profile.user.id))
                embed.description += f"{user} - level {profile.level}, {profile.balance} coins\n"

            await ctx.send(embed=embed)

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return

        with db_session:
            profile = await get_profile(ctx.author.id)
            profile.exp += 1

            # Level up
            if profile.level != (new_level := floor(sqrt(profile.exp) / 4)):
                profile.level = new_level
                bonus = floor(sqrt(profile.level) * 100)
                profile.balance += bonus

                embed = Embed(ctx, title="Level up!")
                embed.set_thumbnail(url=ctx.author.avatar_url)
                embed.description = \
                    f"{ctx.author.mention} levelled up " \
                    f"to **level {profile.level}**. " \
                    f"Level up bonus: **{bonus} points**."

                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Profile(bot))
