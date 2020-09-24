from os import getenv

from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()

        self.prefix: str = getenv("PREFIX", None)
        self.token: str = getenv("TOKEN", None)
        self.status: str = getenv("STATUS", None)
        self.status_type: int = int(getenv("STATUS_TYPE", 0))
        self.db_url: str = getenv("DB_URL", None)
        self.db_user: str = getenv("DB_USER", None)
        self.db_passwd: str = getenv("DB_PASSWD", None)
        self.db_name: str = getenv("DB_NAME", None)
        self.tenor_key: str = getenv("TENOR_KEY", None)
