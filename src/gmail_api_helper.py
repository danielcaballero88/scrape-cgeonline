"""Helper module for the GMAIL API functions."""
import json
import os
import smtplib
from email.message import EmailMessage

HERE = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(HERE)
SECRETS_FILE = os.path.join(BASE_DIR, "secrets", "gmail.json")


def send_gmail(subject, content):
    """Send an email using gmail."""
    # Get account secrets: address and password.
    with open(SECRETS_FILE, "r", encoding="utf-8") as gmail_secrets_file:
        gmail_secrets = json.load(gmail_secrets_file)
        gmail_account = gmail_secrets["account"]
        gmail_password = gmail_secrets["password"]

    # Create email message.
    message = EmailMessage()

    message["To"] = "danielcaballero88@gmail.com"
    message["From"] = "danielcaballero88@gmail.com"
    message["Subject"] = subject
    message.set_content(content)

    # Send email.
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(gmail_account, gmail_password)
        smtp.send_message(message)
