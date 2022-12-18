"""Helper module for the Telegram API."""
import json

import requests

from src.settings import telegram_chat_id, telegram_token


class TelegramBot:
    """A Telegram bot in a single chat.

    The bot reads its configuration from a secret file, getting both the
    bot id from the secret token, and a chat id, meaning that it will be
    linked to this single chat (at least currently).
    """

    def send_telegram_message(self, message: str) -> requests.Response:
        """Send a message to the chat in the config."""
        headers = {
            "Content-Type": "application/json",
            "Proxy-Authorization": "Basic base64",
        }
        data_dict = {
            "chat_id": telegram_chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_notification": True,
        }
        data = json.dumps(data_dict)
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

        response = requests.post(
            url, data=data, headers=headers, verify=False, timeout=10
        )
        return response
