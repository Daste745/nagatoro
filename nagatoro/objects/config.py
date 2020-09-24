import json


class Config:
    def __init__(self, file_path: str):
        with open(file_path) as f:
            data = json.load(f)

        self.testing: bool = data.get("testing", False)
        self.prefix: str = data.get("prefix", None)
        self.token: str = data.get("token", None)
        self.db_url: str = data.get("db_url", None)
        self.db_user: str = data.get("db_user", None)
        self.db_passwd: str = data.get("db_passwd", None)
        self.db_name: str = data.get("db_name", None)
        self.tenor_key: str = data.get("tenor_key", None)
