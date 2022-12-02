"""Test module for the main function 'scrape'."""
import pytest  # pylint: disable=unused-import
from pytest_mock.plugin import MockerFixture

from src import scrape_cgeonline
from tests.mock_response import MockGetResponse


class MockGmail:
    """Mock the gmail api for tests purposes."""

    def __init__(self, expected_subject=None, expected_content=None):
        self.expected_subject = expected_subject
        self.expected_content = expected_content
        self.mock_gmail_create_and_send_draft_times_called = 0

    def mock_gmail_create_and_send_draft(self, subject, content):
        """Mock the method to send an email."""
        self.mock_gmail_create_and_send_draft_times_called += 1

        if self.expected_subject:
            assert subject == self.expected_subject
        if self.expected_content:
            assert content == self.expected_content


def test_scrape_no_changes(mocker: MockerFixture):
    """Test the scrape function when no changes."""
    mock_get_response = mocker.Mock(return_value=MockGetResponse("no_changes"))
    mocker.patch("requests.get", mock_get_response)

    mock_gmail = MockGmail(expected_subject="No new date in cgeonline.")
    mocker.patch(
        "src.scrape_cgeonline.gmail_create_and_send_draft",
        mock_gmail.mock_gmail_create_and_send_draft,
    )
    scrape_cgeonline.scrape(email_every_time=True)

    assert mock_gmail.mock_gmail_create_and_send_draft_times_called == 1


def test_scrape_error(mocker: MockerFixture):
    """Test the scrape function when error."""
    mock_get_response = mocker.Mock(return_value=MockGetResponse("error"))
    mocker.patch("requests.get", mock_get_response)

    mock_gmail = MockGmail(expected_subject="Error scraping cgeonline")
    mocker.patch(
        "src.scrape_cgeonline.gmail_create_and_send_draft",
        mock_gmail.mock_gmail_create_and_send_draft,
    )

    scrape_cgeonline.scrape(email_every_time=True)

    assert mock_gmail.mock_gmail_create_and_send_draft_times_called == 1


def test_scrape_new_date(mocker: MockerFixture):
    """Test the scrape function when new date."""
    mock_get_response = mocker.Mock(return_value=MockGetResponse("new_date"))
    mocker.patch("requests.get", mock_get_response)

    mock_gmail = MockGmail(expected_subject="New date in cgeonline!")
    mocker.patch(
        "src.scrape_cgeonline.gmail_create_and_send_draft",
        mock_gmail.mock_gmail_create_and_send_draft,
    )

    scrape_cgeonline.scrape(email_every_time=True)

    assert mock_gmail.mock_gmail_create_and_send_draft_times_called == 1
