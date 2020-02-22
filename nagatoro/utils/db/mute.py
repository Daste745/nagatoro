from typing import List, Optional
from datetime import timedelta, datetime
from pony.orm import db_session, select
from discord.ext.commands import Context
from discord.ext.commands.errors import CommandError

import nagatoro.objects.database as db
from nagatoro.utils.db import get_user, get_guild


async def make_mute(ctx: Context, user_id: int, time: timedelta,
                    reason: str) -> db.Mute:
    with db_session:
        user = await get_user(user_id)
        guild = await get_guild(ctx.guild.id)

        if not guild.mute_role:
            raise CommandError("This server doesn't have mute role set.")

        mute = db.Mute(
            given_by=ctx.author.id,
            reason=reason,
            user=user,
            guild=guild,
            start=datetime.now(),
            end=datetime.now() + time,
            active=True
        )

        return mute


async def get_mutes(guild_id: int = None, user_id: int = None,
                    active_only: bool = False) -> Optional[List[db.Mute]]:
    with db_session:
        if active_only and not guild_id and not user_id:
            mutes = db.Mute.select(lambda x: x.active)

        elif active_only and guild_id and not user_id:
            mutes = db.Mute.select(
                lambda x: x.active and x.guild.id == guild_id)

        elif not active_only and guild_id and user_id:
            mutes = db.Mute.select(
                lambda x: x.guild.id == guild_id
                and x.user.id == user_id)

        return mutes or None


async def get_active_mute(user_id: int, guild_id: int) -> Optional[db.Mute]:
    with db_session:
        user = await get_user(user_id)

        mute = select(i for i in user.punishments
                      if isinstance(i, db.Mute) and i.guild.id == guild_id
                      and i.active)

        return mute or None


async def is_muted(user_id: int, guild_id: int) -> bool:
    with db_session:
        return True if await get_active_mute(user_id, guild_id) else False
