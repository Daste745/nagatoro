from datetime import datetime
from typing import List

from discord import Role, User
from discord.errors import Forbidden, HTTPException
from discord.ext.tasks import loop
from discord.ext.commands import (
    Cog,
    Context,
    command,
    group,
    cooldown,
    has_permissions,
    bot_has_permissions,
    BucketType,
)

from nagatoro.checks import is_moderator
from nagatoro.objects import Embed
from nagatoro.converters import Member, Timedelta, User as UserC
from nagatoro.db import Guild, User, Moderator, Mute, Warn
from nagatoro.utils import t


class Moderation(Cog):
    """Server moderation"""

    def __init__(self, bot):
        self.bot = bot
        self.check_mutes.start()

    def cog_unload(self):
        self.check_mutes.cancel()

    @group(name="moderators", aliases=["mods"], invoke_without_command=True)
    @cooldown(rate=3, per=30, type=BucketType.guild)
    async def moderators(self, ctx: Context):
        """See who moderates this server

        Everyone on this list can use moderation commands like `mute` and `warn`.
        """

        moderators = Moderator.filter(guild__id=ctx.guild.id).prefetch_related("user")
        if await moderators.count() == 0:
            return await ctx.send(t(ctx, "no_moderators"))

        embed = Embed(ctx, title=t(ctx, "title", guild=ctx.guild), description="")

        await ctx.trigger_typing()
        async for i in moderators:
            user = await self.bot.fetch_user(i.user.id)
            embed.description += f"**{user}** {f'({i.title})' if i.title else ''}\n"

        await ctx.send(embed=embed)

    @moderators.command(name="add")
    @has_permissions(manage_roles=True)
    @cooldown(rate=5, per=30, type=BucketType.guild)
    async def moderators_add(self, ctx: Context, member: Member, *, title: str = None):
        """Add someone to the list of moderators

        `title` is optional and can be used to differentiate between moderator postions.
        """

        if await Moderator.get_or_none(
            user__id=member.id,
            guild__id=ctx.guild.id,
        ):
            return await ctx.send(t(ctx, "already_moderator", member=member))

        user, _ = await User.get_or_create(id=member.id)
        guild, _ = await Guild.get_or_create(id=ctx.guild.id)
        await Moderator.create(guild=guild, user=user, title=title)
        await self.bot.generate_moderator_cache()

        await ctx.send(t(ctx, "message", member=member, guild=ctx.guild))

    @moderators.command(name="add-role")
    @has_permissions(manage_roles=True)
    @cooldown(rate=5, per=30, type=BucketType.guild)
    async def moderators_add_role(self, ctx: Context, role: Role, *, title: str = None):
        """Add members from a role as moderators

        Members who are already moderators are ignored.
        Roles with more than 25 members are disallowed.
        `title` is optional and can be used to differentiate between moderator postions.
        """

        if len(role.members) > 25:
            return await ctx.send(t(ctx, "too_much", limit=25))

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)
        moderators = await Moderator.filter(guild=guild).prefetch_related("user")
        moderator_ids = [i.user.id for i in moderators]
        new_moderators: List[Member] = []

        await ctx.trigger_typing()
        for i in role.members:
            if i.id in moderator_ids:
                continue

            user, _ = await User.get_or_create(id=i.id)
            await Moderator.create(guild=guild, user=user, title=title)
            new_moderators.append(i)

        if len(new_moderators) == 0:
            return await ctx.send(t(ctx, "none_added"))

        await self.bot.generate_moderator_cache()

        await ctx.send(
            t(
                ctx,
                "message",
                amount=len(new_moderators),
                moderators=", ".join(i.name for i in new_moderators),
            )
        )

    @moderators.command(name="delete", aliases=["del"])
    @has_permissions(manage_roles=True)
    @cooldown(rate=5, per=30, type=BucketType.guild)
    async def moderators_delete(self, ctx: Context, member: Member):
        """Remove someone from the list of moderators"""

        if not (
            moderator := await Moderator.get_or_none(
                user__id=member.id, guild__id=ctx.guild.id
            )
        ):
            return await ctx.send(t(ctx, "not_moderator", member=member))

        await moderator.delete()
        await self.bot.generate_moderator_cache()

        await ctx.send(t(ctx, "message", member=member, guild=ctx.guild))

    @group(name="muterole", invoke_without_command=True)
    async def mute_role(self, ctx: Context):
        """Check the mute role

        This is the role given to muted users, it stays with them until the mute ends or they are unmuted manually.
        """

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)
        mute_role = ctx.guild.get_role(guild.mute_role)

        if not guild.mute_role:
            return await ctx.send(t(ctx, "not_set"))
        if not mute_role:
            return await ctx.send(t(ctx, "doesnt_exist"))

        return await ctx.send(
            t(ctx, "message", guild=ctx.guild, name=mute_role, id=mute_role.id)
        )

    @mute_role.command(name="set")
    @has_permissions(manage_roles=True)
    @cooldown(rate=1, per=30, type=BucketType.guild)
    async def mute_role_set(self, ctx: Context, role: Role):
        """Set this server's mute role"""

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)
        guild.mute_role = role.id
        await guild.save()

        await ctx.send(t(ctx, "message", role=role))

    @mute_role.command(name="delete", aliases=["del", "remove", "rm"])
    @has_permissions(manage_roles=True)
    @cooldown(rate=1, per=30, type=BucketType.guild)
    async def mute_role_delete(self, ctx: Context):
        """Remove this server's mute role

        This command DOES NOT delete the role, just removes the mute role setting for this server.
        """

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)
        guild.mute_role = None
        await guild.save()

        await ctx.send(t(ctx, "message", guild=ctx.guild))

    @command(name="ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban(self, ctx: Context, user: UserC, *, reason: str = None):
        """Ban someone

        You can use an ID to ban someone is outside the server.
        To get a user's ID, enable Developer Mode under Appearance Settings, right click on the user's name and select "Copy ID".
        This command does not delete their messages.
        """

        await ctx.guild.ban(
            user=user,
            reason=f"Moderator: {ctx.author}, reason: {reason}",
            delete_message_days=0,
        )

        if reason:
            ban_message = t(ctx, "message_with_reason", user=user, reason=reason)
        else:
            ban_message = t(ctx, "message", user=user)

        await ctx.send(ban_message)

    @command(name="unban", aliases=["pardon"])
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def unban(self, ctx: Context, user: UserC):
        """Unban someone

        Note: Only works with IDs.
        To get a user's ID, enable Developer Mode under Appearance Settings, right click on the user's name and select "Copy ID".
        """

        if user.id not in [i.user.id for i in await ctx.guild.bans()]:
            return await ctx.send(t(ctx, "not_banned", user=user))

        await ctx.guild.unban(user, reason=f"Moderator: {ctx.author}")

        await ctx.send(t(ctx, "message", user=user))

    @group(name="warn", invoke_without_command=True)
    @is_moderator()
    @cooldown(rate=4, per=10, type=BucketType.user)
    async def warn(self, ctx: Context, member: Member, *, reason: str):
        """Warn someone

        Warns do not give any punishments apart fron an entry in the warn list.
        """

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)
        user, _ = await User.get_or_create(id=member.id)
        warn = await Warn.create(
            moderator=ctx.author.id, guild=guild, user=user, reason=reason
        )

        embed = Embed(ctx, title=f"Warn [{warn.id}]", color=member.color)
        embed.description = t(ctx, "message", member=member.mention, reason=reason)

        await ctx.send(embed=embed)

        try:
            await member.send(t(ctx, "dm_message", guild=ctx.guild, reason=reason))
        except (Forbidden, HTTPException, AttributeError):
            pass

    @warn.command(name="delete", aliases=["del", "remove", "rm"])
    @is_moderator()
    @cooldown(rate=4, per=10, type=BucketType.user)
    async def warn_delete(self, ctx: Context, id: int):
        """Delete a warn from the database

        Use the warn id given when muting or viewing someone's warns (the number in square brackets, e.g. [32]).
        """

        if not (warn := await Warn.get_or_none(id=id)):
            return await ctx.send(t(ctx, "doesnt_exist", id=id))

        await warn.fetch_related("guild")
        if warn.guild.id != ctx.guild.id:
            return await ctx.send(t(ctx, "other_guild", id=id))

        await warn.delete()

        await ctx.send(t(ctx, "message", id=id))

    @command(name="warns")
    @cooldown(rate=3, per=15, type=BucketType.guild)
    async def warns(self, ctx: Context, *, member: Member = None):
        """See someone's warns

        If no member specified, this shows Your warns.
        """

        if not member:
            member = ctx.author

        embed = Embed(
            ctx,
            title=t(ctx, "title", member=member),
            description="",
            color=member.color,
        )

        await ctx.trigger_typing()
        warns = Warn.filter(user__id=member.id, guild__id=ctx.guild.id)

        if not await warns.count():
            return await ctx.send(t(ctx, "no_warns", member=member))

        async for i in warns:
            moderator = ctx.bot.get_user(i.moderator)
            # TODO: Format time and use timezones (settings)
            embed.description += (
                f"`{i.id}` {str(i.when.time())[:-10]} "
                f"{i.when.date()} **{moderator}**: *{i.reason}*\n"
            )

        await ctx.send(embed=embed)

    @group(name="mute", invoke_without_command=True)
    @bot_has_permissions(manage_roles=True)
    @is_moderator()
    @cooldown(rate=4, per=10, type=BucketType.user)
    async def mute(
        self, ctx: Context, member: Member, time: Timedelta, *, reason: str = None
    ):
        """Mute someone

        Muting someone gives them the mute role specified by the muterole command and removes the role after the specified time has passed.
        Note: Mutes are checked every 10 seconds, so times are not perfect.
        """

        mute = await Mute.filter(
            user__id=member.id, guild__id=ctx.guild.id, active=True
        ).first()
        if mute:
            mute.end += time
            await mute.save()
            return await ctx.send(t(ctx, "message_extended", member=member, time=time))
            # NOTE: Extensions don't add a mute entry, they just make the
            # active mute longer.
            # return await ctx.send(f"{member.name} is already muted.")

        user, _ = await User.get_or_create(id=member.id)
        guild, _ = await Guild.get_or_create(id=ctx.guild.id)
        if not guild.mute_role:
            return await ctx.send(t(ctx, "no_mute_role", guild=ctx.guild))
        mute = await Mute.create(
            moderator=ctx.author.id,
            user=user,
            guild=guild,
            reason=reason,
            end=datetime.utcnow() + time,
        )

        mute_role = ctx.guild.get_role(guild.mute_role)
        # TODO: Check if member has lower permissions required to mute them
        await member.add_roles(
            mute_role, reason=f"Muted by {ctx.author} for {time}, reason: {reason}"
        )

        embed = Embed(ctx, title=f"Mute [{mute.id}]", color=member.color)
        embed.set_thumbnail(url=member.avatar_url)
        embed.description = t(
            ctx, "message", member=member.mention, time=time, reason=reason
        )

        await ctx.send(embed=embed)

        try:
            await member.send(
                t(ctx, "dm_message", guild=ctx.guild, time=time, reason=reason)
            )
        except (Forbidden, HTTPException, AttributeError):
            pass

    @mute.command(name="delete", aliases=["del", "remove", "rm"])
    @bot_has_permissions(manage_roles=True)
    @is_moderator()
    @cooldown(rate=4, per=10, type=BucketType.user)
    async def mute_delete(self, ctx: Context, id: int):
        """Delete a mute and unmute someone

        Use the mute id given when muting or viewing someone's mutes (the number in square brackets, e.g. [64]).
        """

        if not (mute := await Mute.get_or_none(id=id)):
            return await ctx.send(t(ctx, "doesnt_exist", id=id))

        await mute.fetch_related("guild")
        if mute.guild.id != ctx.guild.id:
            return await ctx.send(t(ctx, "other_guild", id=id))
        await mute.fetch_related("user")
        if (member := ctx.guild.get_member(mute.user.id)) in ctx.guild.members:
            if mute.guild.mute_role:
                # Don't try to remove the mute role if it was unset in settings
                mute_role = ctx.guild.get_role(mute.guild.mute_role)
                await member.remove_roles(mute_role)

        await mute.delete()

        await ctx.send(t(ctx, "message", id=id))

    @command(name="unmute")
    @bot_has_permissions(manage_roles=True)
    @is_moderator()
    @cooldown(rate=4, per=10, type=BucketType.user)
    async def unmute(self, ctx: Context, *, member: Member):
        """Unmute someone

        Manually end someone's mute period.
        """

        mute = await Mute.filter(
            user__id=member.id, guild__id=ctx.guild.id, active=True
        ).first()
        if not mute:
            return await ctx.send(t(ctx, "not_muted", member=member))

        await mute.fetch_related("guild")
        if mute.guild.mute_role:
            mute_role = ctx.guild.get_role(mute.guild.mute_role)
            await member.remove_roles(mute_role)

        mute.active = False
        await mute.save()

        await ctx.send(t(ctx, "message", member=member))

    @group(name="mutes", invoke_without_command=True)
    @cooldown(rate=3, per=15, type=BucketType.guild)
    async def mutes(self, ctx: Context, *, member: Member = None):
        """See someone's mutes

        If no member specified, this shows Your mutes.
        """

        if not member:
            member = ctx.author

        embed = Embed(
            ctx,
            title=t(ctx, "title", member=member),
            description="",
            color=member.color,
        )
        await ctx.trigger_typing()

        mutes = Mute.filter(user__id=member.id, guild__id=ctx.guild.id)
        if not await mutes.count():
            return await ctx.send(t(ctx, "no_mutes", member=member))

        async for i in mutes:
            moderator = await self.bot.fetch_user(i.moderator)
            embed.description += (
                f"`{i.id}` {str(i.start.time())[:-10]} "
                f"{i.start.date()} ({str(i.end - i.start)[:-7]}) "
                f"**{moderator}**: *{i.reason or t(ctx, 'no_reason')}* "
            )
            # TODO: Format time and use timezones
            if i.active:
                embed.description += "🔴"
            embed.description += "\n"

        await ctx.send(embed=embed)

    @mutes.command(name="active")
    @cooldown(rate=2, per=10, type=BucketType.guild)
    async def mutes_active(self, ctx: Context):
        """See active mutes"""

        embed = Embed(ctx, title=t(ctx, "title"))
        await ctx.trigger_typing()

        mutes = Mute.filter(guild__id=ctx.guild.id, active=True)
        if not await mutes.count():
            return await ctx.send(t(ctx, "no_mutes", guild=ctx.guild))

        # TODO: Split active mutes into different embeds when more than 10
        #       and add scrolling (◀️ ▶️)
        async for i in mutes.prefetch_related("user"):
            moderator = ctx.guild.get_member(i.moderator)
            user = ctx.guild.get_member(i.user.id)

            if i.reason:
                description = t(
                    ctx,
                    "entry_with_reason",
                    given_at=f"{str(i.start.time())[:-10]} {str(i.start.date())[5:]}",
                    duration=i.end - i.start,
                    moderator=moderator.mention,
                    reason=i.reason,
                )
            else:
                description = t(
                    ctx,
                    "entry",
                    given_at=f"{str(i.start.time())[:-10]} {str(i.start.date())[5:]}",
                    duration=i.end - i.start,
                    moderator=moderator.mention,
                )

            embed.add_field(name=f"{user} [{i.id}]", value=description, inline=False)

        await ctx.send(embed=embed)

    @loop(seconds=10)
    async def check_mutes(self):
        async for i in Mute.filter(active=True).prefetch_related("guild", "user"):
            if i.end.timestamp() >= datetime.utcnow().timestamp():
                continue

            async def end_mute(mute: Mute):
                mute.active = False
                await mute.save()

            try:
                guild = self.bot.get_guild(i.guild.id)
                assert guild
                mute_role = guild.get_role(i.guild.mute_role)
                assert mute_role
                member = guild.get_member(i.user.id)
                assert member
            except (AttributeError, AssertionError):
                await end_mute(i)
                continue

            try:
                await member.remove_roles(mute_role, reason="Mute ended.")
            except (Forbidden, HTTPException):
                pass

            await end_mute(i)

            try:
                await member.send(f"Your mute in {guild.name} has ended.")
            except (Forbidden, HTTPException, AttributeError):
                pass

    @Cog.listener()
    async def on_member_join(self, member: Member):
        mute = await Mute.get_or_none(
            user__id=member.id, guild__id=member.guild.id, active=True
        )

        if not mute:
            return

        # User joined the guild, has an active mute
        # and doesn't have the mute role, so add it

        await mute.fetch_related("guild")
        guild = self.bot.get_guild(member.guild.id)

        if not (mute_role := guild.get_role(mute.guild.mute_role)):
            return

        if member in guild.members and mute_role not in member.roles:
            await member.add_roles(mute_role)

    @check_mutes.before_loop
    async def before_check_mutes(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Moderation(bot))
