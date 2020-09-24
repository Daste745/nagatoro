import json


class Config:
    def __init__(self, file_path: str):
        with open(file_path) as f:
            data = json.load(f)

        self.prefix: str = data.get("prefix", None)
        self.token: str = data.get("token", None)
        self.status: str = data.get("status", None)
        self.status_type: int = data.get("status_type", 0)
        self.db_url: str = data.get("db_url", None)
        self.db_user: str = data.get("db_user", None)
        self.db_passwd: str = data.get("db_passwd", None)
        self.db_name: str = data.get("db_name", None)
        self.tenor_key: str = data.get("tenor_key", None)
