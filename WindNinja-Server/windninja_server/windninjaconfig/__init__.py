﻿import os
import yaml

from flask_dotenv import DotEnv


class Config:
    DATASTORE = None
    MAIL = {}
    AUTO_REGISTER = {}
    SECRET_KEY = None
    QUEUE = {}

    @classmethod
    def init_app(self, app):
        env = DotEnv()
        env.init_app(app)


__config_file = os.environ["WNSERVER_CONFIG"]
with open(__config_file, "r") as f:
    overrides = yaml.safe_load(f)

Config.DATASTORE = overrides["datastore"]
Config.MAIL.update(overrides["mail"])
Config.AUTO_REGISTER.update(overrides["auto_register"])
Config.QUEUE.update(overrides["queue"])

Config.SECRET_KEY = overrides.get(
    "secret_key", b".\x87\xa4m9\xbd)_\x07\x08{\xf4\xf8qY^\x81\x9f3\xb4U\xca|\x12"
)

Config.MAIL["server"] = {
    "address": os.getenv("AWS_SMTP_HOST"),
    "user": os.getenv("AWS_SMTP_KEY"),
    "password": os.getenv("AWS_SMTP_SECRET"),
}
