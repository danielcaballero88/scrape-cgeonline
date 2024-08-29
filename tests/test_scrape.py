"""Test module for the main function 'scrape'."""

import logging
import pytest  # pylint: disable=unused-import
from pytest_mock.plugin import MockerFixture

from src.scrape_cgeonline.scrape_cgeonline import Scraper
from src.scrape_cgeonline.utils.gmail_api_helper import GmailApiHelper
from src.scrape_cgeonline.utils.telegram_api_helper import TelegramBot
from src.scrape_cgeonline.utils.logging_utils import get_logger

from tests.mock_response import MockGetResponse


class MockGmailApiHelper:
    """Mock the gmail api for tests purposes."""

    def __init__(self, expected_subject=None, expected_content=None):
        self.expected_subject = expected_subject
        self.expected_content = expected_content
        self.mock_send_email_times_called = 0
        self.logger = get_logger("mock_gmail_api_helper", level=logging.DEBUG)

    def send_email(self, subject, content):
        """Mock the method to send an email."""
        self.logger.info("Sending email.")
        self.mock_send_email_times_called += 1

        if self.expected_subject:
            assert subject == self.expected_subject
        if self.expected_content:
            assert content == self.expected_content


class MockTelegramBot:
    """Mock the telegram api class for tests purposes."""

    def __init__(self, expected_message=None):
        self.token = "asd"
        self.chat_id = "123"
        self.expected_message = expected_message
        self.mock_send_telegram_message_times_called = 0
        self.logger = get_logger("mock_telegram_bot", level=logging.DEBUG)

    def send_telegram_message(self, message):
        """Mock the method to send a telegram message."""
        self.logger.info("Sending message to Telegram.")
        self.mock_send_telegram_message_times_called += 1

        if self.expected_message:
            assert message == self.expected_message


def test_scrape_no_changes(mocker: MockerFixture):
    """Test the scrape function when no changes."""
    logger = get_logger("test_scrape_no_changes", level=logging.DEBUG)
    logger.info("Test scrape no changes")
    mock_get_response = mocker.Mock(return_value=MockGetResponse("no_changes"))
    mocker.patch("requests.get", mock_get_response)

    mock_gmail = MockGmailApiHelper(expected_subject="No new date in cgeonline.")
    mocker.patch.object(GmailApiHelper, "send_email", mock_gmail.send_email)

    mock_telegram_bot = MockTelegramBot()
    mocker.patch.object(
        TelegramBot, "send_telegram_message", mock_telegram_bot.send_telegram_message
    )

    scraper = Scraper(email_every_time=True)
    scraper.scrape()

    assert mock_gmail.mock_send_email_times_called == 1
    assert mock_telegram_bot.mock_send_telegram_message_times_called == 1


def test_scrape_error(mocker: MockerFixture):
    """Test the scrape function when error."""
    logger = get_logger("test_scrape_error", level=logging.DEBUG)
    logger.info("Test scrape error")

    mock_get_response = mocker.Mock(return_value=MockGetResponse("error"))
    mocker.patch("requests.get", mock_get_response)

    mock_gmail = MockGmailApiHelper(expected_subject="Error scraping cgeonline")
    mocker.patch.object(GmailApiHelper, "send_email", mock_gmail.send_email)

    mock_telegram_bot = MockTelegramBot()
    mocker.patch.object(
        TelegramBot, "send_telegram_message", mock_telegram_bot.send_telegram_message
    )

    scraper = Scraper(email_every_time=True)
    scraper.scrape()

    assert mock_gmail.mock_send_email_times_called == 1
    assert mock_telegram_bot.mock_send_telegram_message_times_called == 1


def test_scrape_new_date(mocker: MockerFixture):
    """Test the scrape function when new date."""
    mock_get_response = mocker.Mock(return_value=MockGetResponse("new_date"))
    mocker.patch("requests.get", mock_get_response)

    mock_gmail = MockGmailApiHelper(expected_subject="New date in cgeonline!")
    mocker.patch.object(GmailApiHelper, "send_email", mock_gmail.send_email)

    mock_telegram_bot = MockTelegramBot()
    mocker.patch.object(
        TelegramBot, "send_telegram_message", mock_telegram_bot.send_telegram_message
    )

    scraper = Scraper(email_every_time=True)
    scraper.scrape()

    assert mock_gmail.mock_send_email_times_called == 1
    assert mock_telegram_bot.mock_send_telegram_message_times_called == 1
