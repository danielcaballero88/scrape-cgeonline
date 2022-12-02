"""Tests for the cgeonline scraper."""
import os

import pytest  # pylint: disable=unused-import
from pytest_mock.plugin import MockerFixture

from src import scrape_cgeonline

# pylint: disable=protected-access

HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, "data")


class MockGetResponse:
    """Mock response object, reading html from static file."""

    def __init__(self, case: str):
        self.case = case
        response_filename = {
            "no_changes": "test_response_no_changes.html",
            "error": "test_response_error.html",
            "new_date": "test_response_new_date.html",
        }[case]
        self.response_filepath = os.path.join(DATA_DIR, response_filename)

    @property
    def text(self):
        """Mocks requests.response.text."""
        test_response_html = None
        with open(
            file=self.response_filepath, mode="r", encoding="utf-8"
        ) as test_response_file:
            test_response_html = test_response_file.read()
        return test_response_html


def test_scrape_cgeonline_dates_page_no_changes(mocker: MockerFixture):
    """Unit test for a scraping cgeonline dates when no changes."""
    mock_get_response = mocker.Mock(return_value=MockGetResponse("no_changes"))
    mocker.patch("requests.get", mock_get_response)

    scraped_row = scrape_cgeonline._scrape_cgeonline_dates_page()

    assert isinstance(scraped_row, dict)

    assert scraped_row["servicio"] == "Registro Civil-Nacimientos"
    assert scraped_row["ultima_apertura"] == "10/11/2022"
    assert scraped_row["proxima_apertura"] == "fecha por confirmar"
    assert isinstance(scraped_row["solicitud"], str)
    assert scraped_row["solicitud"].startswith("/")
    assert scraped_row["solicitud"].endswith(".html")


def test_scrape_cgeonline_dates_page_error(mocker: MockerFixture):
    """Unit test for scraping cgeonline dates with an error."""
    mock_get_response = mocker.Mock(return_value=MockGetResponse("error"))
    mocker.patch("requests.get", mock_get_response)

    with pytest.raises(ValueError):
        scrape_cgeonline._scrape_cgeonline_dates_page()


def test_scrape_cgeonline_dates_page_new_date(mocker: MockerFixture):
    """Unit test for a scraping cgeonline dates whith a new date."""
    mock_get_response = mocker.Mock(return_value=MockGetResponse("new_date"))
    mocker.patch("requests.get", mock_get_response)

    scraped_row = scrape_cgeonline._scrape_cgeonline_dates_page()

    assert isinstance(scraped_row, dict)

    assert scraped_row["servicio"] == "Registro Civil-Nacimientos"
    assert scraped_row["ultima_apertura"] == "10/11/2022"
    assert scraped_row["proxima_apertura"] == "12/12/2022"
    assert isinstance(scraped_row["solicitud"], str)
    assert scraped_row["solicitud"].startswith("/")
    assert scraped_row["solicitud"].endswith(".html")
