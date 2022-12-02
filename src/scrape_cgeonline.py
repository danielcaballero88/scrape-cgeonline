"""Python module to scrape cgeonline."""
import logging
import os

import requests
from bs4 import BeautifulSoup
from dc_logging import get_logger

from src.gmail_api_helper import gmail_create_and_send_draft

HERE = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(HERE)
LOGFILE = os.path.join(BASE_DIR, "log", "scrape_cgeonline.log")

CGEONLINE_URL = "https://www.cgeonline.com.ar"
DATES_URL = "/informacion/apertura-de-citas.html"

# Root logger defines the file and level for any log propagating up
# the hierarchy. Useful to catch 3rd party libraries warnings and error
# logs.
root_logger = get_logger(
    {
        "file_name": LOGFILE,
        "level": logging.WARNING,
    }
)

# The scraper logger is set up independently so any logging is done
# here is not duplicated by the root logger (propagate = False).
logger = get_logger({"name": "scraper", "file_name": LOGFILE})
logger.propagate = False


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
        or cells[0].text != "Registro Civil-Nacimientos"
        or cells[1].text != "10/11/2022"
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


def scrape(email_every_time: bool):
    """Main function to scrape cgeonline"""
    try:
        row_data = _scrape_cgeonline_dates_page()
    except Exception as exc:
        logger.error(exc)
        gmail_create_and_send_draft(
            subject="Error scraping cgeonline",
            content=str(exc) + "\n\n" + CGEONLINE_URL + DATES_URL,
        )
    else:
        logger.info(row_data)

        if row_data["proxima_apertura"] == "fecha por confirmar":
            logger.info("No new date: %s", row_data)
            if email_every_time:
                gmail_create_and_send_draft(
                    subject="No new date in cgeonline.",
                    content=str(row_data) + "\n\n" + CGEONLINE_URL + DATES_URL,
                )
        else:
            logger.info("New info: %s", row_data)
            gmail_create_and_send_draft(
                subject="New date in cgeonline!",
                content=str(row_data) + "\n\n" + CGEONLINE_URL + DATES_URL,
            )
