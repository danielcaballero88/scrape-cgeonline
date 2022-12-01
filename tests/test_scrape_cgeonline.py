"""Tests for the cgeonline scraper."""
import pytest  # pylint: disable=unused-import
from pytest_mock.plugin import MockerFixture
from src import scrape_cgeonline
import os

# pylint: disable=protected-access

HERE = os.path.dirname(__file__)

class MockGetResponse:
    """Mock response object, reading html from static file."""
    @property
    def text(self):
        """Mocks requests.response.text."""
        test_response_html = None
        with open(
            file=os.path.join(HERE, "test_response.html"),
            mode="r",
            encoding="utf-8"
        ) as test_response_file:
            test_response_html = test_response_file.read()
        return test_response_html


def test_scrape_cgeonline_dates_page(mocker: MockerFixture):
    """Unit test for a single function."""
    mock_get_response = mocker.Mock(return_value=MockGetResponse())
    mocker.patch("requests.get", mock_get_response)

    scraped_row = scrape_cgeonline._scrape_cgeonline_dates_page()

    print(scraped_row)
