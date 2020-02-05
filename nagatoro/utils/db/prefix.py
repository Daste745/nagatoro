from typing import Union
from pony.orm import db_session

from nagatoro.utils.db import get_guild


async def get_prefix(guild_id: int) -> str:
    with db_session:
        guild = await get_guild(guild_id)

        return guild.prefix


async def set_prefix(guild_id: int, prefix: Union[str, None]) -> None:
    with db_session:
        guild = await get_guild(guild_id)
        guild.prefix = prefix

        return guild.prefix
