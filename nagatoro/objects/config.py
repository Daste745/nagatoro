from os import getenv
from typing import Optional

from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()

        self.prefix: Optional[str] = getenv("PREFIX", None)
        self.token: Optional[str] = getenv("TOKEN", None)
        self.status: Optional[str] = getenv("STATUS", None)
        self.status_type: int = int(getenv("STATUS_TYPE", 0))

        self.db_url: str = getenv("DB_URL", "localhost")
        self.db_user: Optional[str] = getenv("DB_USER", None)
        self.db_passwd: Optional[str] = getenv("DB_PASSWD", None)
        self.db_name: Optional[str] = getenv("DB_NAME", None)

        self.redis_url: str = getenv("REDIS_URL", "localhost")
        self.redis_port: str = getenv("REDIS_PORT", "6379")
        self.redis_user: Optional[str] = getenv("REDIS_USER", None)
        self.redis_passwd: Optional[str] = getenv("REDIS_PASSWD", None)

        self.tenor_key: Optional[str] = getenv("TENOR_KEY", None)
