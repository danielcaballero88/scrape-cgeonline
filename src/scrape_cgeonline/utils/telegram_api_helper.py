"""Helper module for the Telegram API."""
import json
import logging

from .logging_utils import get_logger

import requests


class TelegramBot:
    """A Telegram bot in a single chat.

    The bot reads its configuration from a secret file, getting both the
    bot id from the secret token, and a chat id, meaning that it will be
    linked to this single chat (at least currently).
    """
    def __init__(self, telegram_chat_id, telegram_token):
        self.telegram_chat_id = telegram_chat_id
        self.telegram_token = telegram_token
        self.logger = get_logger(name="telegram_bot", level=logging.DEBUG)

    def send_telegram_message(self, message: str) -> requests.Response:
        """Send a message to the chat in the config."""
        self.logger.info("Sending message to Telegram.")
        headers = {
            "Content-Type": "application/json",
            "Proxy-Authorization": "Basic base64",
        }
        data_dict = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_notification": True,
        }
        data = json.dumps(data_dict)
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"

        self.logger.debug(f"Sending message to Telegram: {message}")
        response = requests.post(
            url, data=data, headers=headers, verify=False, timeout=10
        )
        return response
