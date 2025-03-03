import logging
import sys
from logging.handlers import RotatingFileHandler

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"


def setup_logger():
    inner_logger = logging.getLogger("app")
    inner_logger.setLevel(LOG_LEVEL)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    file_handler = RotatingFileHandler("../app.log", maxBytes=10 ** 6, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    inner_logger.addHandler(console_handler)
    inner_logger.addHandler(file_handler)

    return inner_logger


logger = setup_logger()
