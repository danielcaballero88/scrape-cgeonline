"""Helper module for the GMAIL API functions."""
import smtplib
from email.message import EmailMessage

from src.settings import gmail_account, gmail_password


def send_gmail(subject, content):
    """Send an email using gmail."""
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
