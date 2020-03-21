from typing import Optional
from pony.orm import db_session
from discord import Role
from discord.ext.commands import Bot

import nagatoro.objects.database as db


async def get_guild(guild_id: int) -> db.Guild:
    with db_session:
        if not (guild := db.Guild.get(id=guild_id)):
            guild = db.Guild(id=guild_id)

        return guild


async def get_mod_role(bot: Bot, guild_id: int) -> Optional[Role]:
    if not (mod_role_id := (await get_guild(guild_id)).mod_role):
        return

    guild = bot.get_guild(guild_id)

    if not (mod_role := guild.get_role(mod_role_id)):
        return

    return mod_role


async def get_mute_role(bot: Bot, guild_id: int) -> Optional[Role]:
    if not (mute_role_id := (await get_guild(guild_id)).mute_role):
        return

    guild = bot.get_guild(guild_id)

    if not (mute_role := guild.get_role(mute_role_id)):
        return

    return mute_role
