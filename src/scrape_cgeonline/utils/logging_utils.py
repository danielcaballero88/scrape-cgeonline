"""Utils module for logging."""
import logging
import os
import sys
import traceback

from .config import config
from .get_package_dir import get_package_dir


HERE = os.path.dirname(__file__)
PKG_DIR = get_package_dir()
os.makedirs(os.path.join(PKG_DIR, "log"), exist_ok=True)
LOGFILE = os.path.join(PKG_DIR, "log", "scrape_cgeonline.log")


def exc_to_str(exception: Exception) -> str:
    """Take an exception and return the traceback in a string."""
    _exc_type, _exc_obj, _exc_tb = sys.exc_info()
    exception_str = str(exception) + "\n" + traceback.format_exc()
    return exception_str


def get_logging_formatter(*tags) -> logging.Formatter:
    """Get a predefined logging formatter."""
    logging_tags = {
        "time": "%(asctime)s",
        "name": "%(name)-12s",
        "file": "%(filename)s",
        "function": "%(funcName)-12s",
        "level": "%(levelname)-12s",
    }

    if not tags:
        _tags: tuple[str, ...] = ("time", "name", "file", "function", "level")
    else:
        _tags = tags

    tag_strings: list[str] = []

    for tag in _tags:
        tag_strings.append(logging_tags[tag])

    formatter_str = " : ".join(tag_strings) + " :: %(message)s"

    formatter = logging.Formatter(formatter_str)

    return formatter


loggers: dict[str, logging.Logger] = {}


def _get_logger(name: str, level: int, propagate: bool) -> logging.Logger:
    if name in loggers:
        return loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(level)
    # if not logger.hasHandlers():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(get_logging_formatter())
    logger.addHandler(console_handler)
    file_handler = logging.FileHandler(LOGFILE, mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(get_logging_formatter())
    logger.addHandler(file_handler)

    logger.propagate = propagate

    loggers[name] = logger

    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger."""
    if not name or name == "scraper":
        name = "scraper"
        propagate = False
    else:
        # Make sure the root scraper logger exists first
        _get_logger("scraper", level=config.logging_level, propagate=False)
        name = "scraper." + name
        propagate = True

    logger = _get_logger(name=name, level=config.logging_level, propagate=propagate)

    return logger
