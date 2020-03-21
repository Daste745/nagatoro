from math import sqrt, floor, ceil
from datetime import datetime, timedelta
from asyncio import TimeoutError
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
            # TODO: Add global rank to profile
            embed.add_fields(
                ("Level", f"{profile.level}"),
                ("Experience", f"{profile.exp}/{next_level_exp} "
                               f"({progress}%)"),
                ("Balance", f"{profile.balance} coins"),
                ("Mutes", str(len(mutes))),
                ("Warns", str(len(warns)))
            )

        await ctx.send(embed=embed)

    @command(name="balance", aliases=["bal", "money"])
    async def balance(self, ctx: Context, *, member: Member = None):
        """Coin balance"""

        if not member:
            member = ctx.author
        
        with db_session:
            profile = await get_profile(member.id)
            embed = Embed(ctx, title=f"{member.name}'s balance",
                          description=f"Balance: **{profile.balance} coins**",
                          color=member.color)

        await ctx.send(embed=embed)

    @command(name="level", aliases=["lvl"])
    async def level(self, ctx: Context, *, member: Member = None):
        """User's level"""

        if not member:
            member = ctx.author

        profile = await get_profile(member.id)
        embed = Embed(ctx, title=f"{member.name}'s level", color=member.color,
                      description=f"Level: **{profile.level}**")

        await ctx.send(embed=embed)

    @group(name="ranking", aliases=["top"], invoke_without_command=True)
    @cooldown(rate=2, per=20, type=BucketType.guild)
    async def ranking(self, ctx: Context):
        """User ranking"""

        await self.ranking_level.__call__(ctx)

    @ranking.command(name="level", aliases=["lvl"])
    async def ranking_level(self, ctx: Context):
        """Top users by level"""

        await ctx.trigger_typing()
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
    async def ranking_balance(self, ctx: Context):
        """Top users by balance"""

        await ctx.trigger_typing()
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
        """Give coins to someone"""

        if member == ctx.author:
            raise BadArgument("You can't transfer money to yourself.")
        if amount <= 0:
            raise BadArgument("Transfer amount can't be zero or negative.")

        with db_session:
            if balance := (await get_profile(ctx.author.id)).balance < amount:
                raise BadArgument(f"Not enough funds, you have only "
                                  f"{balance} coins.")

        embed = Embed(ctx, title="Transfer")
        embed.description = f"You are about to give **{amount}** coin(s) " \
                            f"to {member.mention}, are you sure?"
        message = await ctx.send(embed=embed)
        await message.add_reaction("✅")

        try:
            await self.bot.wait_for("reaction_add", timeout=30,
                                    check=lambda r, u: u == ctx.message.author
                                    and str(r.emoji) == "✅")
        except TimeoutError:
            embed.description = "Transfer cancelled."
            return await message.edit(embed=embed)
        finally:
            await message.clear_reactions()

        with db_session:
            profile = await get_profile(ctx.author.id)
            target_profile = await get_profile(member.id)
            profile.balance -= amount
            target_profile.balance += amount

            embed.description = f"Transferred **{amount}** coin(s) " \
                                f"to {member.mention}"
            await message.edit(embed=embed)

    @command(name="daily")
    async def daily(self, ctx: Context, member: Member = None):
        """Daily coin reward

        Mention someone to give your reward to them.
        Can be used once every 23 hours.
        Streak gives you more coins over time, but will be lost
        after 2 days of inactivity.
        """

        with db_session:
            profile = await get_profile(ctx.author.id)

            if profile.last_daily and \
                    profile.last_daily + timedelta(hours=23) > datetime.now():
                next_daily = timedelta(hours=23) - \
                             (datetime.now() - profile.last_daily)
                return await ctx.send(
                    f"Your next daily will be available in "
                    f"**{ceil(next_daily.seconds / 3600)} hour(s)**. "
                    f"Current streak: **{profile.daily_streak}**.")

            target_profile = await get_profile(member.id) if member else profile

            if profile.daily_streak and \
                    datetime.now() - profile.last_daily < timedelta(days=2):
                profile.daily_streak += 1
            else:
                profile.daily_streak = 1

            profile.last_daily = datetime.now()
            bonus = floor(sqrt(profile.daily_streak) * 20)
            target_profile.balance += 100 + bonus

            embed = Embed(ctx, title="Daily", color=ctx.author.color)
            if target_profile == profile:
                embed.description = \
                    f"You got **{100 + bonus}** daily points.\n" \
                    f"Streak: **{profile.daily_streak}**."
            else:
                embed.description = \
                    f"You gave your **{100 + bonus}** daily points " \
                    f"to {member.mention}\n" \
                    f"Streak: **{profile.daily_streak}**"

            await ctx.send(embed=embed)

    @Cog.listener()
    async def on_message(self, message: Message):
        if self.bot.config.testing:
            return
        if message.author.bot:
            return
        # TODO: Make better spam filter.
        if len(message.content) <= 5:
            return
        if "spam" in message.channel.name.lower():
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

                if profile.level < 5:
                    return

                embed = Embed(ctx, title="Level up!")
                embed.set_thumbnail(url=ctx.author.avatar_url)
                embed.description = \
                    f"Congratulations, {ctx.author.mention}! " \
                    f"You have advanced to **level {profile.level}** " \
                    f"and got a bonus of **{bonus} points**."

                level_up_message = await ctx.send(embed=embed)
                await level_up_message.delete(delay=30)


def setup(bot):
    bot.add_cog(Profile(bot))
