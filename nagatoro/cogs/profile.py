from math import sqrt, floor
from pony.orm import db_session, select
from discord import Message, Color
from discord.ext.commands import Cog, Context, command, group, cooldown, \
    BucketType, BadArgument

import nagatoro.objects.database as db
from nagatoro.converters import Member
from nagatoro.objects import Embed
from nagatoro.utils.db import get_profile


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
            # Calculate current level progress from proportions:
            # (exp - curr lvl req) * 100 / (curr lvl req - next lvl req)
            current_level_exp = (profile.level * 4) ** 2
            next_level_exp = ((profile.level + 1) * 4) ** 2
            progress = round((profile.exp - current_level_exp) * 100 /
                             (next_level_exp - current_level_exp))

            embed = Embed(
                ctx, title=f"{member.name}'s profile", color=member.color)
            embed.set_thumbnail(url=member.avatar_url)
            mutes = select(i for i in profile.user.punishments
                           if isinstance(i, db.Mute)).without_distinct()
            warns = select(i for i in profile.user.punishments
                           if isinstance(i, db.Warn)).without_distinct()
            embed.add_fields(
                ("Level", f"{profile.level}"),
                ("Experience", f"{profile.exp}/{next_level_exp} "
                               f"({progress}%)"),
                ("Balance", f"{profile.balance} coins"),
                ("Mutes", str(len(mutes))),
                ("Warns", str(len(warns)))
            )

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

    @group(name="ranking", aliases=["top"])
    @cooldown(rate=2, per=20, type=BucketType.guild)
    async def ranking(self, ctx: Context):
        """User ranking"""

        if ctx.invoked_subcommand:
            return
        await self.level.__call__(ctx)

    @ranking.command(name="level", aliases=["lvl"])
    async def level(self, ctx: Context):
        """Top users by level"""

        with db_session:
            top_users = \
                db.Profile.select().order_by(db.desc(db.Profile.exp))[:10]

            embed = Embed(ctx, title="Level ranking", description="",
                          color=Color.blue())
            for profile in top_users:
                user = await self.bot.fetch_user(profile.user.id)
                embed.description += \
                    f"{user.mention}: **{profile.level}** level\n"

            await ctx.send(embed=embed)

    @ranking.command(name="balance", aliases=["bal", "money"])
    async def balance(self, ctx: Context):
        """Top users by balance"""

        with db_session:
            top_users = \
                db.Profile.select().order_by(db.desc(db.Profile.balance))[:10]

            embed = Embed(ctx, title="Balance ranking", description="",
                          color=Color.blue())
            for profile in top_users:
                user = await self.bot.fetch_user(profile.user.id)
                embed.description += \
                    f"{user.mention}: **{profile.balance}** coins\n"

            await ctx.send(embed=embed)

    @command(name="transfer", aliases=["give", "pay"])
    @cooldown(rate=2, per=10, type=BucketType.user)
    async def transfer(self, ctx: Context, amount: int, *, member: Member):
        """Transfer coins to another member"""

        with db_session:
            profile = await get_profile(ctx.author.id)

            if member == ctx.author:
                raise BadArgument("You can't transfer money to yourself.")
            if amount <= 0:
                raise BadArgument("Transfer amount can't be zero or negative.")
            if profile.balance < amount:
                raise BadArgument(f"Not enough funds, you have only "
                                  f"{profile.balance} coins.")

            target_profile = await get_profile(member.id)
            profile.balance -= amount
            target_profile.balance += amount

            embed = Embed(ctx, title="Transfer")
            embed.description = f"Transferred **{amount}** coin(s) from" \
                                f" {ctx.author.mention} to {member.mention}."
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

                level_up_message = await ctx.send(embed=embed)
                await level_up_message.delete(delay=15)


def setup(bot):
    bot.add_cog(Profile(bot))
