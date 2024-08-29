"""Settings module."""
import os
import logging
from enum import Enum

from dotenv import find_dotenv, load_dotenv

from .logging_utils import get_logger
from .get_package_dir import get_package_dir


class Environment(str, Enum):
    development = "development"
    production = "production"


class Config:
    def __init__(self):
        self.logger = get_logger(name="config", level=logging.DEBUG)
        self.load_env_vars()

    def load_env_vars(self):
        """Load environment variables.

        If an env file exists, it will override any values already
        set as environment variables.
        """
        PKG_DIR = get_package_dir()
        ENV_FILE = os.path.join(PKG_DIR, "secrets", ".env")
        self.logger.debug(
            "\nPKG_DIR: %s\n"
            "ENV_FILE: %s",
            PKG_DIR,
            ENV_FILE,
        )

        env_file = find_dotenv(ENV_FILE)
        self.logger.debug("Loading environment variables from %s", env_file)
        load_dotenv(env_file)

    @property
    def environment(self) -> Environment:
        environment_str = os.environ.get("ENVIRONMENT", "development")
        if environment_str not in ["development", "production"]:
            raise ValueError("ENVIRONMENT must be 'development' or 'production'.")
        return Environment(environment_str)

    @property
    def gmail_account(self):
        if not os.environ.get("GMAIL_ACCOUNT"):
            raise ValueError("GMAIL_ACCOUNT not set.")
        return os.environ.get("GMAIL_ACCOUNT")

    @property
    def gmail_password(self):
        if not os.environ.get("GMAIL_PASSWORD"):
            raise ValueError("GMAIL_PASSWORD not set.")
        return os.environ.get("GMAIL_PASSWORD")

    @property
    def telegram_token(self):
        if not os.environ.get("TELEGRAM_TOKEN"):
            raise ValueError("TELEGRAM_TOKEN not set.")
        return os.environ.get("TELEGRAM_TOKEN")

    @property
    def telegram_chat_id(self):
        if not os.environ.get("TELEGRAM_CHAT_ID"):
            raise ValueError("TELEGRAM_CHAT_ID not set.")
        return os.environ.get("TELEGRAM_CHAT_ID")
