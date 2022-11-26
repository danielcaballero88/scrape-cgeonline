"""Helper module for the GMAIL API functions."""
import base64
import os
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

HERE = os.path.dirname(__file__)
TOKEN_FILE = os.path.join(HERE, "token.json")
CREDENTIALS_FILE = os.path.join(HERE, "credentials.json")

# https://developers.google.com/gmail/api/auth/scopes
SCOPES = [
    # "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]


def gmail_create_and_send_draft(subject, content):
    """Create a gmail draft and send it."""
    # Authentication
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    # Create and send draft.
    try:
        # create gmail api client
        service = build("gmail", "v1", credentials=creds)

        message = EmailMessage()

        message["To"] = "danielcaballero88@gmail.com"
        message["From"] = "danielcaballero88@gmail.com"
        message["Subject"] = subject
        message.set_content(content)

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"message": {"raw": encoded_message}}
        # pylint: disable=E1101
        draft = (
            service.users().drafts().create(userId="me", body=create_message).execute()
        )

        print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')

        service.users().drafts().send(userId="me", body={"id": draft["id"]}).execute()

    except HttpError as error:
        print(f"An error occurred: {error}")
        draft = None

    return draft
