"""Python module to scrape cgeonline."""
import datetime as dt
import logging
import os
import re

import requests
from bs4 import BeautifulSoup
from dc_logging import get_logger

from src.gmail_api_helper import send_gmail
from src.logging_utils import exc_to_str
from src.telegram_api_helper import TelegramBot

HERE = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(HERE)
LOGFILE = os.path.join(BASE_DIR, "log", "scrape_cgeonline.log")

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
config_file = os.path.join(BASE_DIR, "secrets", "telegram.json")
telegram_bot = TelegramBot(config_file=config_file)


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
        ValueError: If there is any error during the scraping that may
        mean that the page structure has changed.
    """
    result = {}

    req = requests.get(CGEONLINE_URL + DATES_URL, timeout=10)
    soup = BeautifulSoup(req.text, features="html.parser")

    rows = soup.find_all(
        lambda x: x.name == "tr" and "Registro Civil-Nacimientos" in x.text
    )

    if not rows:
        # No rows selected means some error finding the correct row.
        raise ValueError(
            f"No row for 'Registro Civil-Nacimientos' found in {CGEONLINE_URL + DATES_URL}"
        )

    row = rows[0]
    cells = row.find_all("td")
    if (
        not cells
        or not re.search(
            re.compile(pattern="registro civil.*nacimiento", flags=re.IGNORECASE),
            cells[0].text,
        )
        or not re.search(
            re.compile(pattern=r"1\s?/\s?12\s?/\s?(20)?22"),
            cells[1].text,
        )
    ):
        # Some discrepancy between the expected information in the row
        # and the actual information scraped.
        raise ValueError(f"Row data is not as expected: {row}")

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


def scrape(email_every_time: bool):
    """Main function to scrape cgeonline"""
    try:
        row_data = _scrape_cgeonline_dates_page()
    except Exception as exc:
        logger.error("Error while scraping cgeonline: %s", exc)
        send_notification(
            subject="Error scraping cgeonline",
            content=NOW + "\n\n" + str(exc) + "\n\n" + CGEONLINE_URL + DATES_URL,
        )
    else:
        logger.debug("Scraped data from the target row: %s", row_data)

        if re.search(
            re.compile(r"fecha\s?por\s?confirmar", flags=re.IGNORECASE),
            row_data["proxima_apertura"],
        ):
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
                content=NOW
                + "\n\n"
                + str(row_data)
                + "\n\n"
                + CGEONLINE_URL
                + DATES_URL,
            )
