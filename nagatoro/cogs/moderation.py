from datetime import datetime
from pony.orm import db_session
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

import nagatoro.objects.database as db
from nagatoro.checks import is_moderator
from nagatoro.objects import Embed
from nagatoro.converters import Member, Timedelta
from nagatoro.utils.db import (
    get_warns,
    make_warn,
    get_guild,
    get_mutes,
    make_mute,
    get_mod_role,
    get_mute_role,
    is_muted,
)


class Moderation(Cog):
    """Server moderation"""

    def __init__(self, bot):
        self.bot = bot
        self.check_mutes.start()

    def cog_unload(self):
        self.check_mutes.cancel()

    @group(name="modrole", invoke_without_command=True)
    async def mod_role(self, ctx: Context):
        """Check the moderator role

        This role permits users who have it to perform moderator actions, like muting or warning.
        """

        if not (mod_role := await get_mod_role(self.bot, ctx.guild.id)):
            return await ctx.send(
                "This guild doesn't have mod role set or it was deleted."
            )

        return await ctx.send(
            f"{ctx.guild.name}'s moderator role: **{mod_role.name}** (id: `{mod_role.id}`)"
        )

    @mod_role.command(name="set")
    @has_permissions(manage_roles=True)
    @cooldown(rate=1, per=30, type=BucketType.guild)
    async def mod_role_set(self, ctx: Context, role: Role):
        """Set this server's moderator role"""

        with db_session:
            guild = await get_guild(ctx.guild.id)
            guild.mod_role = role.id

        await ctx.send(f"Set the mod role to **{role.name}**.")

    @mod_role.command(name="delete", aliases=["del", "remove"])
    @has_permissions(manage_roles=True)
    @cooldown(rate=1, per=30, type=BucketType.guild)
    async def mod_role_delete(self, ctx: Context):
        """Remove this server's mod role

        It is recommended to use use this before deleting the role.
        This command DOES NOT delete the role, just removes the mod role setting for this server.
        """

        with db_session:
            guild = await get_guild(ctx.guild.id)
            guild.mod_role = None

        await ctx.send(f"Removed the mod role from {ctx.guild.name}.")

    @group(name="muterole", invoke_without_command=True)
    async def mute_role(self, ctx: Context):
        """Check the mute role

        This is the role given to muted users, it stays with them until the mute ends or they are unmuted manually.
        """

        if not (mute_role := await get_mute_role(self.bot, ctx.guild.id)):
            return await ctx.send(
                "This guild doesn't have mute role set or it was deleted."
            )

        return await ctx.send(
            f"{ctx.guild.name}'s mute role: **{mute_role.name}** (id: `{mute_role.id}`)"
        )

    @mute_role.command(name="set")
    @has_permissions(manage_roles=True)
    @cooldown(rate=1, per=30, type=BucketType.guild)
    async def mute_role_set(self, ctx: Context, role: Role):
        """Set this server's mute role"""

        with db_session:
            guild = await get_guild(ctx.guild.id)
            guild.mute_role = role.id

        await ctx.send(f"Set the mute role to **{role.name}**.")

    @mute_role.command(name="delete", aliases=["del", "remove"])
    @has_permissions(manage_roles=True)
    @cooldown(rate=1, per=30, type=BucketType.guild)
    async def mute_role_delete(self, ctx: Context):
        """Remove this server's mute role

        It is recommended to use use this before deleting the role.
        This command DOES NOT delete the role, just removes the mute role setting for this server.
        """

        with db_session:
            guild = await get_guild(ctx.guild.id)
            guild.mute_role = None

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

        await ctx.guild.ban(user=user, reason=reason, delete_message_days=0)

        ban_message = f"Banned {user}"
        if reason:
            ban_message += f", reason: *{reason}*."

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
        Note: Some emojis get corrupted in the process of saving, so try not to use them until this issue is fixed.
        """

        # FIXME: Database does not save emoji properly
        warn = await make_warn(ctx, member.id, reason)

        embed = Embed(ctx, title=f"Warn [{warn.id}]", color=member.color)
        embed.description = f"Warned {member.mention}, reason: *{reason}*"

        await ctx.send(embed=embed)

        try:
            await member.send(
                f"You have been warned in **{ctx.guild.name}**, " f"reason: *{reason}*"
            )
        except (Forbidden, AttributeError):
            pass

    @warn.command(name="delete", aliases=["del", "remove"])
    @is_moderator()
    @cooldown(rate=4, per=10, type=BucketType.user)
    async def warn_delete(self, ctx: Context, id: int):
        """Delete a warn from the database

        Use the warn id given when muting or viewing someone's warns (the number in square brackets, e.g. [32]).
        """

        with db_session:
            if not (warn := db.Warn[id]):
                return await ctx.send(f"A Warn with ID **{id}** doesn't exist.")

            if warn.guild.id != ctx.guild.id:
                return await ctx.send(
                    f"The warn with id `{id}` is from another server. "
                    f"You can't change or delete it."
                )

            warn.delete()

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

        with db_session:
            if not (warns := await get_warns(member.id, ctx.guild.id)):
                return await ctx.send(
                    f"{member.name} doesn't have any warns on this server."
                )

            for i in reversed(warns[:15]):
                moderator = self.bot.get_user(i.given_by)
                embed.description += (
                    f"`{i.id}` **{moderator}:** {i.when} - *{i.reason}*\n"
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
        Note: Some emojis get corrupted in the process of saving, so try not to use them until this issue is fixed.
        Note: Mutes are checked every 15 seconds,
        so muting someone for 5 seconds would probably turn
        into a 15 second mute.
        """

        if await is_muted(member.id, ctx.guild.id):
            # TODO: Mute time extension
            return await ctx.send(f"{member.name} is already muted.")

        # FIXME: Database does not recognise emoji
        mute = await make_mute(ctx, member.id, time, reason)

        mute_role = await get_mute_role(self.bot, ctx.guild.id)
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

    @mute.command(name="delete", aliases=["del", "remove"])
    @bot_has_permissions(manage_roles=True)
    @is_moderator()
    @cooldown(rate=4, per=10, type=BucketType.user)
    async def mute_delete(self, ctx: Context, id: int):
        """Delete a mute and unmute someone

        Use the mute id given when muting or viewing someone's mutes (the number in square brackets, e.g. [64]).
        """

        with db_session:
            if not (mute := db.Mute[id]):
                return await ctx.send(f"A Mute with ID **{id}** doesn't exist.")

            if mute.guild.id != ctx.guild.id:
                return await ctx.send(
                    f"The mute with id `{id}` is from another server. "
                    f"You can't change or delete it."
                )

            member = ctx.guild.get_member(mute.user.id)

            if member in ctx.guild.members:
                mute_role = ctx.guild.get_role(mute.guild.mute_role)
                await member.remove_roles(mute_role)

            mute.delete()

            await ctx.send(f"Removed mute `{id}` from the database.")

    @command(name="unmute")
    @bot_has_permissions(manage_roles=True)
    @is_moderator()
    @cooldown(rate=4, per=10, type=BucketType.user)
    async def unmute(self, ctx: Context, *, member: Member):
        """Unmute someone

        Manually end someone's mute period.
        """

        with db_session:
            mute = await get_mutes(
                active_only=True, user_id=member.id, guild_id=ctx.guild.id
            )
            if not mute:
                return await ctx.send(f"{member.name} is not muted.")

            mute_role = ctx.guild.get_role(mute.guild.mute_role)
            await member.remove_roles(mute_role)
            mute.active = False

            await ctx.send(f"Unmuted {member.name}")

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

        with db_session:
            if not (mutes := await get_mutes(ctx.guild.id, member.id)):
                return await ctx.send(
                    f"{member.name} doesn't have any mutes on this server."
                )

            for i in reversed(mutes[:15]):
                moderator = await self.bot.fetch_user(i.given_by)
                embed.description += (
                    f"`{i.id}` **{moderator}**: {i.start} - "
                    f"{i.end - i.start} - *{i.reason or 'No reason'}* "
                )
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

        with db_session:
            if not (mutes := await get_mutes(ctx.guild.id, active_only=True)):
                return await ctx.send(f"There are no active mutes in {ctx.guild.name}.")

            # TODO: Split active mutes into different embeds when more than 10
            #       and add scrolling (◀️ ▶️)
            for i in reversed(mutes[:10]):
                moderator = await self.bot.fetch_user(i.given_by)
                user = await self.bot.fetch_user(i.user.id)
                embed.add_field(
                    name=f"{user} [{i.id}]",
                    value=f"**Given at**: {i.start}\n"
                    f"**Duration**: {i.end - i.start}\n"
                    f"**Moderator**: {moderator.mention}\n"
                    f"**Reason**: *{i.reason or 'No reason'}*",
                )

        await ctx.send(embed=embed)

    @loop(seconds=10)
    async def check_mutes(self):
        with db_session:
            mutes = await get_mutes(active_only=True)

            if not mutes:
                return

            for i in mutes:
                if i.end >= datetime.now():
                    continue

                # Mute ended, remove role and notify in DM's

                guild = self.bot.get_guild(i.guild.id)
                mute_role = guild.get_role(i.guild.mute_role)
                member = guild.get_member(i.user.id)

                if member in guild.members:
                    try:
                        await member.remove_roles(mute_role, reason="Mute ended.")
                    except Forbidden:
                        pass
                i.active = False

                try:
                    await member.send(f"Your mute in {guild.name} has ended.")
                except (Forbidden, HTTPException, AttributeError):
                    pass

    @Cog.listener()
    async def on_member_join(self, member: Member):
        with db_session:
            mute = await get_mutes(
                guild_id=member.guild.id, user_id=member.id, active_only=True
            )

            if not mute:
                return

            # User joined the guild, has an active mute
            # and doesn't have the mute role, add it

            guild = self.bot.get_guild(member.guild.id)
            mute_role = guild.get_role(mute.guild.mute_role)

            if member in guild.members and mute_role not in member.roles:
                await member.add_roles(mute_role)

    @check_mutes.before_loop
    async def before_check_mutes(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Moderation(bot))
