"""Python module to scrape cgeonline."""

import datetime as dt
import json
import logging
import os
import re
import time

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from dc_logging import get_logger

from .config import Config
from .utils.gmail_api_helper import GmailApiHelper
from .utils.logging_utils import exc_to_str
from .utils.scraping_error import ScrapingError
from .utils.telegram_api_helper import TelegramBot


HERE = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(HERE)
LOGFILE = os.path.join(BASE_DIR, "log", "scrape_cgeonline.log")
os.makedirs(os.path.join(BASE_DIR, "log"), exist_ok=True)
LAST_DATA_FILE = os.path.join(BASE_DIR, "log", "last_data.json")

CGEONLINE_URL = "https://www.cgeonline.com.ar"
DATES_URL = "/informacion/apertura-de-citas.html"

# # Root logger defines the file and level for any log propagating up
# # the hierarchy. Useful to catch 3rd party libraries warnings and error
# # logs.
# root_logger = get_logger(
#     level=logging.WARNING,
#     file_output=True,
#     file_name=LOGFILE,
# )

class Scraper:
    def __init__(
            self,
            email_every_time: bool = False,
            verbose: bool = False,
        ) -> None:
        self.email_every_time = email_every_time

        # The scraper logger is the main logger (top parent) of the scraper app,
        # it's set up independently from the root logger so any logging done
        # here is not duplicated by the root logger (propagate = False).
        self.logger = get_logger(
            name="scraper",
            level=logging.DEBUG,
            file_name=LOGFILE,
            file_output=True,
            file_level=logging.DEBUG,
            propagate=False,
        )
        if verbose:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s : %(name)-12s : %(funcName)-12s : %(levelname)-12s :: "
                    "%(message)s"
                )
            )
            self.logger.addHandler(console_handler)


        # Telegram bot object.
        self.telegram_bot = TelegramBot(
            telegram_chat_id=Config.telegram_chat_id, telegram_token=Config.telegram_token
        )

        # Gmail API helper object.
        self.gmail_api_helper = GmailApiHelper(
            gmail_account=Config.gmail_account, gmail_password=Config.gmail_password
        )

    def _scrape_cgeonline_dates_page(self):
        """Get the info for new appointments for births registering.

        Returns:
            A dictionary with the row info:
                {
                    'servicio': ,
                    'ultima_apertura': ,
                    'proxima_apertura': ,
                    'solicitud': ,
                }

        Raises:
            ScrapingError: If there is any error during the scraping that may
            mean that the page structure has changed.
        """
        result = {}

        max_retries = 5
        num_retries = 0
        while num_retries <= max_retries:
            resp = requests.get(CGEONLINE_URL + DATES_URL, timeout=10)

            if resp.ok:
                break

            time.sleep(30)
            num_retries += 1
            self.logger.debug(
                "Bad response (%s), retrying... %s/%s",
                resp.status_code,
                num_retries,
                max_retries,
            )

        if resp.status_code == 525:
            # Special case, I'm getting quite a few of these.
            raise ScrapingError(
                f"525 status code (SSL Certificates Error) in {CGEONLINE_URL + DATES_URL}",
                resp,
            )

        if not resp.ok:
            raise ScrapingError(
                f"Bad response trying to scrape {CGEONLINE_URL + DATES_URL}", resp
            )

        soup = BeautifulSoup(resp.text, features="html.parser")

        def _match_row_regex(element: Tag) -> bool:
            if element.name == "tr" and re.search(
                re.compile(pattern="registro civil.*nacimiento", flags=re.IGNORECASE),
                element.text,
            ):
                return True

            return False

        rows = soup.find_all(_match_row_regex)

        if not rows:
            # No rows selected means some error finding the correct row.
            raise ScrapingError(
                f"No row for 'Registro Civil-Nacimientos' found in {CGEONLINE_URL + DATES_URL}",
                resp,
            )

        row = rows[0]
        cells = row.find_all("td")
        if not cells or not re.search(
            re.compile(pattern="registro civil.*nacimiento", flags=re.IGNORECASE),
            cells[0].text,
        ):
            # Some discrepancy between the expected information in the row
            # and the actual information scraped.
            raise ScrapingError(f"Row data is not as expected: {row}", resp)

        # Being here there is no error during scraping.
        result = {
            "servicio": cells[0].text,
            "ultima_apertura": cells[1].text,
            "proxima_apertura": cells[2].text,
            "solicitud": cells[3].a.get("href"),
        }

        return result


    def send_notification(self, subject, content):
        """Send notification to all the channels."""
        self.logger.info(
            "Attempting to send notifications with subject=%s and content=%s",
            subject,
            content,
        )
        try:
            GmailApiHelper.send_email(subject=subject, content=content)
        except Exception as exc:
            self.logger.error("Error trying to send gmail notification: %s", exc)
            self.logger.debug("Traceback: %s", exc_to_str(exc))

        try:
            self.telegram_bot.send_telegram_message(f"{subject}\n\n{content}")
        except Exception as exc:
            self.logger.error("Error trying to send telegram notification: %s", exc)
            self.logger.debug("Traceback: %s", exc_to_str(exc))


    def scrape(self):
        """Main function to scrape cgeonline"""
        NOW = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            row_data = self._scrape_cgeonline_dates_page()
        except ScrapingError as exc:
            self.logger.error("Error while scraping cgeonline: %s", exc)
            self.send_notification(
                subject="Error scraping cgeonline",
                content=NOW
                + "\n\n"
                + str(exc)
                + "\n\n"
                + CGEONLINE_URL
                + DATES_URL
                + "\n\n"
                + exc.response,
            )
            return 1
        except Exception as exc:
            self.logger.error("Unexpected error while trying to scrape cgeonline: %s", exc)
            self.send_notification(
                subject="Error in cgeonline scraper :(",
                content=NOW + "\n\n" + str(exc) + "\n\n" + CGEONLINE_URL + DATES_URL,
            )
            return 1

        # If here, scraping was successful.

        self.logger.debug("Scraped data from the target row: %s", row_data)

        if os.path.exists(LAST_DATA_FILE):
            with open(file=LAST_DATA_FILE, mode="r", encoding="utf-8") as json_file:
                last_data = json.load(json_file)
        else:
            # This would mean a first run if the file doesn't exist, so I just take the
            # currently scraped data.
            last_data = row_data

        if row_data == last_data:
            self.logger.info("No new date: %s", row_data)
            if self.email_every_time:
                self.send_notification(
                    subject="No new date in cgeonline.",
                    content=NOW
                    + "\n\n"
                    + str(row_data)
                    + "\n\n"
                    + CGEONLINE_URL
                    + DATES_URL,
                )
        else:
            self.logger.info("New info: %s", row_data)
            self.send_notification(
                subject="New date in cgeonline!",
                content=NOW + "\n\n" + str(row_data) + "\n\n" + CGEONLINE_URL + DATES_URL,
            )

        with open(file=LAST_DATA_FILE, mode="w", encoding="utf-8") as json_file:
            json.dump(row_data, json_file, indent=2)
