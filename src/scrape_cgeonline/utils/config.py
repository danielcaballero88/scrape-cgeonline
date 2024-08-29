"""Settings module."""
import os
from enum import Enum

from dotenv import find_dotenv, load_dotenv

from .get_package_dir import get_package_dir


class Environment(str, Enum):
    development = "development"
    production = "production"


class Config:
    def __init__(self):
        self.load_env_vars()

    def load_env_vars(self):
        """Load environment variables.

        If an env file exists, it will override any values already
        set as environment variables.
        """
        PKG_DIR = get_package_dir()
        ENV_FILE = os.path.join(PKG_DIR, "secrets", ".env")
        env_file = find_dotenv(ENV_FILE)
        load_dotenv(env_file)

    @property
    def environment(self) -> Environment:
        environment_str = os.environ.get("ENVIRONMENT", "development")
        if environment_str not in ["development", "production"]:
            raise ValueError("ENVIRONMENT must be 'development' or 'production'.")
        return Environment(environment_str)

    @property
    def gmail_account(self) -> str | None:
        if not os.environ.get("GMAIL_ACCOUNT"):
            raise ValueError("GMAIL_ACCOUNT not set.")
        return os.environ.get("GMAIL_ACCOUNT")

    @property
    def gmail_password(self) -> str | None:
        if not os.environ.get("GMAIL_PASSWORD"):
            raise ValueError("GMAIL_PASSWORD not set.")
        return os.environ.get("GMAIL_PASSWORD")

    @property
    def telegram_token(self) -> str | None:
        if not os.environ.get("TELEGRAM_TOKEN"):
            raise ValueError("TELEGRAM_TOKEN not set.")
        return os.environ.get("TELEGRAM_TOKEN")

    @property
    def telegram_chat_id(self) -> str | None:
        if not os.environ.get("TELEGRAM_CHAT_ID"):
            raise ValueError("TELEGRAM_CHAT_ID not set.")
        return os.environ.get("TELEGRAM_CHAT_ID")

    @property
    def logging_level(self) -> str:
        return os.environ.get("LOGGING_LEVEL", "INFO")

    @property
    def logfile(self) -> str | None:
        return os.environ.get("LOGFILE")


config = Config()
