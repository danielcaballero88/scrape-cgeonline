"""Helper module for the GMAIL API functions."""
import logging

from .logging_utils import get_logger

import smtplib
from email.message import EmailMessage


class GmailApiHelper:
    """Helper class for the GMAIL API functions."""
    def __init__(self, gmail_account, gmail_password):
        self.gmail_account = gmail_account
        self.gmail_password = gmail_password
        self.logger = get_logger(name="gmail_api_helper", level=logging.DEBUG)

    def send_email(self, subject, content):
        """Send an email using gmail."""
        self.logger.info("Sending email.")
        # Create email message.
        message = EmailMessage()
        message["To"] = "danielcaballero88@gmail.com"
        message["From"] = "danielcaballero88@gmail.com"
        message["Subject"] = subject
        message.set_content(content)

        # Send email.
        self.logger.debug(f"Sending email: {subject} - {content}")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.gmail_account, self.gmail_password)
            smtp.send_message(message)
