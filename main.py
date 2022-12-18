"""Entry point script to scrape cgeonline."""
import argparse

from src.scrape_cgeonline import scrape


def _parse_arguments():
    """Parse passed arguments and return args Namespace."""
    parser = argparse.ArgumentParser("")
    parser.add_argument(
        "--email-every-time",
        dest="email_every_time",
        action="store_true",
        help="Sends email for every execution even it there is no new info.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="The program logs to console."
    )
    parsed_args = parser.parse_args()
    return parsed_args


if __name__ == "__main__":
    args = _parse_arguments()
    scrape(email_every_time=args.email_every_time, verbose=args.verbose)
