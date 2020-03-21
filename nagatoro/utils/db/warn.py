from typing import List, Optional
from pony.orm import db_session, select
from datetime import datetime
from discord.ext.commands import Context

import nagatoro.objects.database as db
from nagatoro.utils.db import get_user, get_guild


async def make_warn(ctx: Context, user_id: int, reason: str) -> db.Warn:
    with db_session:
        user = await get_user(user_id)
        guild = await get_guild(ctx.guild.id)
        warn = db.Warn(
            given_by=ctx.author.id,
            reason=reason,
            user=user,
            guild=guild,
            when=datetime.now()
        )

        return warn


async def get_warns(user_id: int, guild_id: int) -> Optional[List[db.Warn]]:
    with db_session:
        user = await get_user(user_id)
        warns = select(
            i for i in user.punishments
            if isinstance(i, db.Warn) and i.guild.id == guild_id
        ).without_distinct()

        return warns if warns else None
