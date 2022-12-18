"""Settings module."""
import os

from dotenv import find_dotenv, load_dotenv

HERE = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(HERE)
ENV_FILE = os.path.join(BASE_DIR, "secrets", ".env")

env_file = find_dotenv(ENV_FILE)
load_dotenv(env_file)

gmail_account = os.environ.get("GMAIL_ACCOUNT")
gmail_password = os.environ.get("GMAIL_PASSWORD")

telegram_token = os.environ.get("TELEGRAM_TOKEN")
telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
