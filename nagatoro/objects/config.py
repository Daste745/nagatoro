import json
from typing import IO


class Config:
    def __init__(self, prefix: str, token: str, db_url: str, db_user: str, db_passwd: str, db_name: str):
        self.prefix = prefix
        self.token = token
        self.db_url = db_url
        self.db_user = db_user
        self.db_passwd = db_passwd
        self.db_name = db_name

    @classmethod
    def from_file(cls, file: IO):
        data = json.load(file)
        return Config(
            prefix=data["prefix"],
            token=data["token"],
            db_url=data["db_url"],
            db_user=data["db_user"],
            db_passwd=data["db_passwd"],
            db_name=data["db_name"]
        )
