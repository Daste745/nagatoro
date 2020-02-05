from pony.orm import db_session
import nagatoro.objects.database as db


async def get_guild(guild_id: int) -> db.Guild:
    with db_session:
        if not (guild := db.Guild.get(id=guild_id)):
            guild = db.Guild(id=guild_id)

        return guild
