from pony.orm import db_session

import nagatoro.objects.database as db
from nagatoro.utils.db import get_user


async def get_profile(user_id: int) -> db.Profile:
    with db_session:
        user = await get_user(user_id)
        if not (profile := db.Profile.get(user=user)):
            profile = db.Profile(user=user, exp=0, level=0, balance=0)

    return profile
