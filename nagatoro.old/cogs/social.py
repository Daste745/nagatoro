from math import sqrt, floor, ceil
from datetime import datetime

from asyncio import TimeoutError
from discord import Message, Color
from discord.errors import Forbidden
from discord.ext.commands import (
    Cog,
    Context,
    command,
    group,
    cooldown,
    BucketType,
)

from nagatoro.converters import Member
from nagatoro.objects import Embed
from nagatoro.utils import aenumerate, t, tg
from nagatoro.db import Guild, User, Mute, Warn


class Social(Cog):
    """Social commands"""

    def __init__(self, bot):
        self.bot = bot

    @command(name="profile")
    @cooldown(rate=2, per=10, type=BucketType.user)
    async def profile(self, ctx: Context, *, member: Member = None):
        """User's profile"""

        if not member:
            member = ctx.author

        user, _ = await User.get_or_create(id=member.id)
        # Calculate current level progress:
        # (exp - curr lvl req) * 100 / (curr lvl req - next lvl req)
        current_level_exp = (user.level * 4) ** 2
        next_level_exp = ((user.level + 1) * 4) ** 2
        progress = round(
            (user.exp - current_level_exp) * 100 / (next_level_exp - current_level_exp)
        )
        # Find position of profile in global user ranking
        rank = (await User.all().order_by("-exp")).index(user)

        embed = Embed(
            ctx, title=t(ctx, "title", member=member.name), color=member.color
        )
        embed.set_thumbnail(url=member.avatar_url)

        embed.add_fields(
            (t(ctx, "rank"), str(rank + 1)),
            (t(ctx, "level"), f"{user.level}"),
            (t(ctx, "experience"), f"{user.exp}/{next_level_exp} ({progress}%)"),
            (t(ctx, "balance"), t(ctx, "balance_value", bal=user.balance)),
        )

        if mutes := await Mute.filter(
            guild__id=ctx.guild.id, user__id=member.id
        ).count():
            embed.add_field(name=t(ctx, "mutes"), value=str(mutes))
        if warns := await Warn.filter(
            guild__id=ctx.guild.id, user__id=member.id
        ).count():
            embed.add_field(name=t(ctx, "warns"), value=str(warns))

        await ctx.send(embed=embed)

    @command(name="balance", aliases=["bal", "money"])
    @cooldown(rate=5, per=10, type=BucketType.user)
    async def balance(self, ctx: Context, *, member: Member = None):
        """Coin balance"""

        if not member:
            member = ctx.author

        user, _ = await User.get_or_create(id=member.id)
        await ctx.send(t(ctx, "messsage", member=member.name, bal=user.balance))

    @command(name="level", aliases=["lvl"])
    @cooldown(rate=5, per=10, type=BucketType.user)
    async def level(self, ctx: Context, *, member: Member = None):
        """User's level"""

        if not member:
            member = ctx.author

        user, _ = await User.get_or_create(id=member.id)
        await ctx.send(t(ctx, "message", member=member.name, lvl=user.level))

    @group(name="ranking", aliases=["top", "baltop"], invoke_without_command=True)
    @cooldown(rate=2, per=30, type=BucketType.guild)
    async def ranking(self, ctx: Context):
        """User ranking

        Use 'baltop' for quicker access to the balance ranking
        """

        if ctx.invoked_with == "baltop":
            ctx.command = self.ranking_balance
            return await self.ranking_balance(ctx)

        ctx.command = self.ranking_level
        await self.ranking_level(ctx)

    @ranking.command(name="level", aliases=["lvl"])
    @cooldown(rate=2, per=30, type=BucketType.guild)
    async def ranking_level(self, ctx: Context):
        """User ranking, by level"""

        embed = Embed(ctx, title=t(ctx, "title"), description="", color=Color.blue())

        await ctx.trigger_typing()
        async for pos, i in aenumerate(User.all().order_by("-exp").limit(10), start=1):
            user = await self.bot.fetch_user(i.id)
            embed.description += t(
                ctx, "ranking_entry", pos=pos, user=user, lvl=i.level, exp=i.exp
            )

        await ctx.send(embed=embed)

    @ranking.command(name="balance", aliases=["bal", "money"])
    @cooldown(rate=2, per=30, type=BucketType.guild)
    async def ranking_balance(self, ctx: Context):
        """User ranking, sorted by balance"""

        embed = Embed(ctx, title=t(ctx, "title"), description="", color=Color.blue())

        await ctx.trigger_typing()
        async for pos, i in aenumerate(
            User.all().order_by("-balance").limit(10), start=1
        ):
            user = await self.bot.fetch_user(i.id)
            embed.description += t(
                ctx, "ranking_entry", pos=pos, user=user, lvl=i.level, exp=i.exp
            )

        await ctx.send(embed=embed)

    @command(name="pay", aliases=["give", "transfer"])
    @cooldown(rate=2, per=10, type=BucketType.user)
    async def pay(self, ctx: Context, amount: int, *, member: Member):
        """Give coins to someone

        You can't give money to yourself or any bots.
        Transfer amount should be more than 0.
        """

        if member == ctx.author or member.bot:
            return await ctx.send(t(ctx, "other_users_only"))
        if amount <= 0:
            return await ctx.send(t(ctx, "at_least_one"))

        user, _ = await User.get_or_create(id=ctx.author.id)

        if user.balance < amount:
            return await ctx.send(
                t(
                    ctx,
                    "not_enough_funds",
                    coins=user.balance,
                    missing=amount - user.balance,
                )
            )

        embed = Embed(
            ctx,
            title=t(ctx, "title"),
            description=t(ctx, "confirmation", amount=amount, member=member.mention),
        )
        message = await ctx.send(embed=embed)
        await message.add_reaction("✅")

        try:
            await self.bot.wait_for(
                "reaction_add",
                timeout=30,
                check=lambda r, u: u == ctx.message.author and str(r.emoji) == "✅",
            )
        except TimeoutError:
            embed.description = t(ctx, "cancelled")
            return await message.edit(embed=embed)

        target_user, _ = await User.get_or_create(id=member.id)
        user.balance -= amount
        target_user.balance += amount
        await user.save()
        await target_user.save()

        try:
            await message.clear_reactions()
        except Forbidden:
            pass

        embed.description = t(ctx, "success", amount=amount, member=member.mention)
        await message.edit(embed=embed)

    @command(name="daily", aliases=["dly"])
    async def daily(self, ctx: Context, member: Member = None):
        """Daily coin reward

        Mention someone to give your them your reward.
        Can be used once every 23 hours.
        Streak gives you more coins over time, but will be lost after 2 days of inactivity.
        """

        if member and member.bot:
            return await ctx.send(t(ctx, "cannot_give_to_bot"))

        user, _ = await User.get_or_create(id=ctx.author.id)

        def hours_til_next_daily() -> int:
            return ceil(
                (user.next_daily.timestamp() - datetime.utcnow().timestamp()) / 3600
            )

        if not user.daily_available:
            try:
                await ctx.send(
                    t(
                        ctx,
                        "next_daily",
                        remaining=hours_til_next_daily(),
                        streak=user.daily_streak,
                    )
                )
            except Forbidden:
                pass
            return

        expired = t(ctx, "lost_streak") if user.daily_streak_expired else ""
        if user.daily_streak_expired:
            user.daily_streak = 1
        else:
            user.daily_streak += 1

        bonus = floor(sqrt(user.daily_streak) * 20)
        user.last_daily = datetime.utcnow()

        if member:
            target_user, _ = await User.get_or_create(id=member.id)
        else:
            target_user = user
        target_user.balance += 100 + bonus

        await user.save()
        if user != target_user:
            await target_user.save()

        embed = Embed(ctx, title=t(ctx, "title"), color=ctx.author.color)
        if user == target_user:
            embed.description = t(
                ctx,
                "received_daily",
                amount=100 + bonus,
                streak=user.daily_streak,
                expired=expired,
                remaining=hours_til_next_daily(),
            )

        else:
            embed.description = t(
                ctx,
                "gave_daily",
                amount=100 + bonus,
                member=member.mention,
                streak=user.daily_streak,
                expired=expired,
                remaining=hours_til_next_daily(),
            )

        try:
            await ctx.send(embed=embed)
        except Forbidden:
            pass

    @Cog.listener()
    async def on_message(self, message: Message):
        if (
            message.author.bot
            or not message.guild
            or len(message.content) <= 5
            or "spam" in message.channel.name.lower()
        ):
            # TODO: Make better spam filter.
            return

        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return

        user, _ = await User.get_or_create(id=ctx.author.id)
        user.exp += 1
        await user.save()

        if user.level != (new_level := floor(sqrt(user.exp) / 4)):
            user.level = new_level
            bonus = floor(sqrt(user.level) * 100)
            user.balance += bonus
            await user.save()

            if user.level < 5:
                return

            # Level up message, don't send if the guild has them turned off
            guild, _ = await Guild.get_or_create(id=ctx.guild.id)
            if not guild.level_up_messages:
                return

            try:
                await ctx.send(
                    tg(
                        ctx,
                        "level_up_message",
                        user=ctx.author.name,
                        level=user.level,
                        bonus=bonus,
                    )
                )
            except Forbidden:
                pass

            # TODO: Let the admin choose if they want embed or text level ups
            # embed = Embed(ctx, title="Level up!")
            # embed.set_thumbnail(url=ctx.author.avatar_url)
            # embed.description = (
            #     f"Congratulations, {ctx.author.mention}! "
            #     f"You have advanced to **level {user.level}** "
            #     f"and got a bonus of **{bonus} points**."
            # )
            #
            # level_up_message = await ctx.send(embed=embed)
            # await level_up_message.delete(delay=30)


def setup(bot):
    bot.add_cog(Social(bot))
