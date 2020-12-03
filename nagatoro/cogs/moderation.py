from datetime import datetime
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
from nagatoro.converters import Member, Timedelta
from nagatoro.db import Guild, User, Moderator, Mute, Warn


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
            return await ctx.send(
                f"There are no moderators on this server. "
                f"See `{self.bot.config.prefix}help moderators` for more info."
            )

        embed = Embed(ctx, title=f"Moderators of {ctx.guild}", description="")

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
            return await ctx.send(f"**{member}** is already a moderator!")

        user, _ = await User.get_or_create(id=member.id)
        guild, _ = await Guild.get_or_create(id=ctx.guild.id)
        await Moderator.create(guild=guild, user=user, title=title)

        await ctx.send(f"Saved **{member}** as a moderator of **{ctx.guild}**.")

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
            return await ctx.send(
                f"**{member}** is not a moderator, "
                f"you can't delete them from the list!"
            )

        await moderator.delete()

        await ctx.send(f"Removed **{member}** from **{ctx.guild}**'s moderators.")

    @group(name="muterole", invoke_without_command=True)
    async def mute_role(self, ctx: Context):
        """Check the mute role

        This is the role given to muted users, it stays with them until the mute ends or they are unmuted manually.
        """

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)
        mute_role = ctx.guild.get_role(guild.mute_role)

        if not guild.mute_role:
            return await ctx.send("The mute role is not set on this server.")
        if not mute_role:
            return await ctx.send("The mute role on this server doesn't exist.")

        return await ctx.send(
            f"{ctx.guild.name}'s mute role: **{mute_role.name}** (id: `{mute_role.id}`)"
        )

    @mute_role.command(name="set")
    @has_permissions(manage_roles=True)
    @cooldown(rate=1, per=30, type=BucketType.guild)
    async def mute_role_set(self, ctx: Context, role: Role):
        """Set this server's mute role"""

        guild, _ = await Guild.get_or_create(id=ctx.guild.id)
        guild.mute_role = role.id
        await guild.save()

        await ctx.send(f"Set the mute role to **{role.name}**.")

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

        await ctx.send(f"Removed the mute role from {ctx.guild.name}.")

    @command(name="ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban(self, ctx: Context, user: User, *, reason: str = None):
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
            ban_message = f"Banned {user}, reason: *{reason}*."
        else:
            ban_message = f"Banned {user}"

        await ctx.send(ban_message)

    @command(name="unban", aliases=["pardon"])
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def unban(self, ctx: Context, user: User):
        """Unban someone

        Note: Only works with IDs.
        To get a user's ID, enable Developer Mode under Appearance Settings, right click on the user's name and select "Copy ID".
        """

        if user.id not in [i.user.id for i in await ctx.guild.bans()]:
            return await ctx.send(f"{user} is not banned.")

        await ctx.guild.unban(user, reason=f"Moderator: {ctx.author}")

        await ctx.send(f"Unbanned {user}")

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
        embed.description = f"Warned {member.mention}, reason: *{reason}*"

        await ctx.send(embed=embed)

        try:
            await member.send(
                f"You have been warned in **{ctx.guild.name}**, "
                f"reason: *{warn.reason}*"
            )
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
            return await ctx.send(f"A Warn with ID **{id}** doesn't exist.")

        await warn.fetch_related("guild")
        if warn.guild.id != ctx.guild.id:
            return await ctx.send(
                f"The warn with id `{id}` is from another server. "
                f"You can't change or delete it."
            )

        await warn.delete()

        await ctx.send(f"Removed warn `{id}` from the database.")

    @command(name="warns")
    @cooldown(rate=3, per=15, type=BucketType.guild)
    async def warns(self, ctx: Context, *, member: Member = None):
        """See someone's warns

        If no member specified, this shows Your warns.
        """

        if not member:
            member = ctx.author

        embed = Embed(
            ctx, title=f"{member.name}'s warns", description="", color=member.color
        )

        await ctx.trigger_typing()
        warns = Warn.filter(user__id=member.id, guild__id=ctx.guild.id)

        if not await warns.count():
            return await ctx.send(
                f"{member.name} doesn't have any warns on this server."
            )

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
            return await ctx.send(f"Extended {member.name}'s mute by {time}.")
            # NOTE: Extensions don't add a mute entry, they just make the
            # active mute longer.
            # return await ctx.send(f"{member.name} is already muted.")

        user, _ = await User.get_or_create(id=member.id)
        guild, _ = await Guild.get_or_create(id=ctx.guild.id)
        if not guild.mute_role:
            return await ctx.send(
                f"**{ctx.guild}** has no mute role set. "
                f"See help for the `muterole` command for more info."
            )
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
        embed.description = f"Muted {member.mention} for {time}\n" f"Reason: *{reason}*"

        await ctx.send(embed=embed)

        try:
            await member.send(
                f"You have been muted in **{ctx.guild.name}** "
                f"for {time}, reason: *{reason}*"
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
            return await ctx.send(f"A Mute with ID **{id}** doesn't exist.")

        await mute.fetch_related("guild")
        if mute.guild.id != ctx.guild.id:
            return await ctx.send(
                f"The mute with id `{id}` is from another server. "
                f"You can't change or delete it."
            )

        await mute.fetch_related("user")
        if (member := ctx.guild.get_member(mute.user.id)) in ctx.guild.members:
            if mute.guild.mute_role:
                # Don't try to remove the mute role if it was unset in settings
                mute_role = ctx.guild.get_role(mute.guild.mute_role)
                await member.remove_roles(mute_role)

        await mute.delete()

        await ctx.send(f"Removed mute `{id}` from the database.")

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
            return await ctx.send(f"{member.name} is not muted.")

        await mute.fetch_related("guild")
        if mute.guild.mute_role:
            mute_role = ctx.guild.get_role(mute.guild.mute_role)
            await member.remove_roles(mute_role)

        mute.active = False
        await mute.save()

        await ctx.send(f"Unmuted **{member.name}**.")

    @group(name="mutes", invoke_without_command=True)
    @cooldown(rate=3, per=15, type=BucketType.guild)
    async def mutes(self, ctx: Context, *, member: Member = None):
        """See someone's mutes

        If no member specified, this shows Your mutes.
        """

        if not member:
            member = ctx.author

        embed = Embed(
            ctx, title=f"{member.name}'s mutes", description="", color=member.color
        )
        await ctx.trigger_typing()

        mutes = Mute.filter(user__id=member.id, guild__id=ctx.guild.id)
        if not await mutes.count():
            return await ctx.send(
                f"{member.name} doesn't have any mutes on this server."
            )

        async for i in mutes:
            moderator = await self.bot.fetch_user(i.moderator)
            embed.description += (
                f"`{i.id}` {str(i.start.time())[:-10]} "
                f"{i.start.date()} ({str(i.end - i.start)[:-7]}) "
                f"**{moderator}**: *{i.reason or 'No reason'}* "
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

        embed = Embed(ctx, title="Active mutes")
        await ctx.trigger_typing()

        mutes = Mute.filter(guild__id=ctx.guild.id, active=True)
        if not await mutes.count():
            return await ctx.send(f"There are no active mutes in **{ctx.guild.name}**.")

        # TODO: Split active mutes into different embeds when more than 10
        #       and add scrolling (◀️ ▶️)
        async for i in mutes.prefetch_related("user"):
            moderator = ctx.guild.get_member(i.moderator)
            user = ctx.guild.get_member(i.user.id)

            description = (
                f"**Given at**: {str(i.start.time())[:-10]} {str(i.start.date())[5:]}\n"
                f"**Duration**: {str(i.end - i.start)[:-7]}\n"
                f"**Moderator**: {moderator.mention}"
            )
            if i.reason:
                description += f"\n**Reason**: *{i.reason}*"

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
