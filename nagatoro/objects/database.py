from datetime import datetime
from pony.orm import *

from nagatoro.objects import Config


db = Database()

with open("data/config.json", "r") as file:
    config = Config.from_file(file)
db.bind(
    provider="mysql",
    host=config.db_url,
    user=config.db_user,
    passwd=config.db_passwd,
    db=config.db_name)


class Snowflake(db.Entity):
    id = PrimaryKey(int, size=64, unsigned=True)


class Guild(Snowflake):
    prefix = Optional(str, nullable=True)
    lang = Optional(str, nullable=True)
    mod_role = Optional(int, size=64, unsigned=True)
    mute_role = Optional(int, size=64, unsigned=True)
    punishments = Set('Punishment')


class Punishment(db.Entity):
    id = PrimaryKey(int, auto=True)
    given_by = Required(int, size=64)
    reason = Optional(str)
    user = Required('User')
    guild = Required(Guild)


class User(Snowflake):
    punishments = Set(Punishment)
    profile = Optional('Profile')


class Warn(Punishment):
    start = Required(datetime)
    end = Required(datetime)
    active = Required(bool)


class Mute(Punishment):
    when = Required(datetime)


class Profile(db.Entity):
    id = PrimaryKey(int, auto=True)
    exp = Required(int, unsigned=True)
    level = Required(int, unsigned=True)
    balance = Required(int)
    user = Required(User)


db.generate_mapping()
