"""Shared module for a mock response class."""
import logging
import os

from src.scrape_cgeonline.utils.logging_utils import get_logger

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
        self.logger = get_logger("mock_get_response", level=logging.DEBUG)

    @property
    def text(self):
        """Mocks requests.response.text."""
        self.logger.debug("Accesing MockGetResponse.text.")
        test_response_html = None
        with open(
            file=self.response_filepath, mode="r", encoding="utf-8"
        ) as test_response_file:
            test_response_html = test_response_file.read()
        return test_response_html

    @property
    def ok(self):
        self.logger.debug("Accesing MockGetResponse.ok.")
        if self.case == "error":
            self.logger.debug("Returning False.")
            return False
        self.logger.debug("Returning True.")
        return True

    @property
    def status_code(self):
        self.logger.debug("Accesing MockGetResponse.status_code.")
        if self.case == "error":
            return 404
        return 200

    def __str__(self):
        return f"MockGetResponse({self.case})"
