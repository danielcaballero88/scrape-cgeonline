"""Helper module for the Telegram API."""
import json

import requests


class TelegramBot:
    """A Telegram bot in a single chat.

    The bot reads its configuration from a secret file, getting both the
    bot id from the secret token, and a chat id, meaning that it will be
    linked to this single chat (at least currently).
    """

    def __init__(self, config_file: str):
        self.token, self.chat_id = self.get_telegram_conf(config_file)

    def get_telegram_conf(self, config_file: str):
        """Read bot configuration from a secret file."""
        with open(file=config_file, mode="r", encoding="utf-8") as telegram_conf_file:
            telegram_data = json.load(telegram_conf_file)
        telegram_token = telegram_data["token"]
        telegram_chat_id = telegram_data["chat_id"]
        return telegram_token, telegram_chat_id

    def send_telegram_message(self, message: str) -> requests.Response:
        """Send a message to the chat in the config."""
        headers = {
            "Content-Type": "application/json",
            "Proxy-Authorization": "Basic base64",
        }
        data_dict = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_notification": True,
        }
        data = json.dumps(data_dict)
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        response = requests.post(
            url, data=data, headers=headers, verify=False, timeout=10
        )
        return response
