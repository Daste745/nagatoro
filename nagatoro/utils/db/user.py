from pony.orm import db_session

import nagatoro.objects.database as db


async def get_user(user_id: int) -> db.User:
    with db_session:
        if not (user := db.User.get(id=user_id)):
            user = db.User(id=user_id)

        return user
