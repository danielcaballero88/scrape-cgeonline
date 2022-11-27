import pytest
from pytest_mock.plugin import MockerFixture
import scrape_cgeonline

class MockGetResponse:
    @property
    def text(self):
        test_response_html = None
        with open("test_response.html", "r", encoding="utf-8") as test_response_file:
            test_response_html = test_response_file.read()
        return test_response_html


def test_scrape_cgeonline_dates_page(mocker: MockerFixture):
    mock_get_response = mocker.Mock(return_value=MockGetResponse())
    mocker.patch("requests.get", mock_get_response)

    scraped_row = scrape_cgeonline.scrape_cgeonline_dates_page()

    print(scraped_row)
