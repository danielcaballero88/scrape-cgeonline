"""Python script to scrape cgeonline."""

import requests
from bs4 import BeautifulSoup
from dc_logging import get_logger

CGEONLINE_URL = "https://www.cgeonline.com.ar"
DATES_URL = "/informacion/apertura-de-citas.html"

logger = get_logger({"file_name": "scrape-cgeonline.log"})


def scrape_cgeonline_dates_page():
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
    html_string = str(req.content, "windows-1250")
    soup = BeautifulSoup(html_string, features="html.parser")

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


if __name__ == "__main__":
    try:
        row_data = scrape_cgeonline_dates_page()
        logger.info(row_data)
    except Exception as exc:
        logger.error(exc)
