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

from src.gmail_api_helper import send_gmail
from src.logging_utils import exc_to_str
from src.scraping_error import ScrapingError
from src.telegram_api_helper import TelegramBot

HERE = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(HERE)
LOGFILE = os.path.join(BASE_DIR, "log", "scrape_cgeonline.log")
LAST_DATA_FILE = os.path.join(BASE_DIR, "log", "last_data.json")

CGEONLINE_URL = "https://www.cgeonline.com.ar"
DATES_URL = "/informacion/apertura-de-citas.html"

NOW = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Root logger defines the file and level for any log propagating up
# the hierarchy. Useful to catch 3rd party libraries warnings and error
# logs.
root_logger = get_logger(
    level=logging.WARNING,
    file_output=True,
    file_name=LOGFILE,
)

# The scraper logger is the main logger (top parent) of the scraper up,
# it's set up independently from the root logger so any logging done
# here is not duplicated by the root logger (propagate = False).
logger = get_logger(
    name="scraper",
    level=logging.DEBUG,
    file_name=LOGFILE,
    file_output=True,
    file_level=logging.DEBUG,
    propagate=False,
)

# Telegram bot object.
telegram_bot = TelegramBot()


def _scrape_cgeonline_dates_page():
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
        logger.debug(
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


def send_notification(subject, content):
    """Send notification to all the channels."""
    logger.info(
        "Attempting to send notifications with subject=%s and content=%s",
        subject,
        content,
    )
    try:
        send_gmail(subject=subject, content=content)
    except Exception as exc:
        logger.error("Error trying to send gmail notification: %s", exc)
        logger.debug("Traceback: %s", exc_to_str(exc))

    try:
        telegram_bot.send_telegram_message(f"{subject}\n\n{content}")
    except Exception as exc:
        logger.error("Error trying to send telegram notification: %s", exc)
        logger.debug("Traceback: %s", exc_to_str(exc))


def scrape(email_every_time: bool = False, verbose: bool = False):
    """Main function to scrape cgeonline"""
    if verbose:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s : %(name)-12s : %(funcName)-12s : %(levelname)-12s :: "
                "%(message)s"
            )
        )
        logger.addHandler(console_handler)

    try:
        row_data = _scrape_cgeonline_dates_page()
    except ScrapingError as exc:
        logger.error("Error while scraping cgeonline: %s", exc)
        send_notification(
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
        logger.error("Unexpected error while trying to scrape cgeonline: %s", exc)
        send_notification(
            subject="Error in cgeonline scraper :(",
            content=NOW + "\n\n" + str(exc) + "\n\n" + CGEONLINE_URL + DATES_URL,
        )
        return 1

    # If here, scraping was successful.

    logger.debug("Scraped data from the target row: %s", row_data)

    if os.path.exists(LAST_DATA_FILE):
        with open(file=LAST_DATA_FILE, mode="r", encoding="utf-8") as json_file:
            last_data = json.load(json_file)
    else:
        # This would mean a first run if the file doesn't exist, so I just take the
        # currently scraped data.
        last_data = row_data

    if row_data == last_data:
        logger.info("No new date: %s", row_data)
        if email_every_time:
            send_notification(
                subject="No new date in cgeonline.",
                content=NOW
                + "\n\n"
                + str(row_data)
                + "\n\n"
                + CGEONLINE_URL
                + DATES_URL,
            )
    else:
        logger.info("New info: %s", row_data)
        send_notification(
            subject="New date in cgeonline!",
            content=NOW + "\n\n" + str(row_data) + "\n\n" + CGEONLINE_URL + DATES_URL,
        )

    with open(file=LAST_DATA_FILE, mode="w", encoding="utf-8") as json_file:
        json.dump(row_data, json_file, indent=2)
