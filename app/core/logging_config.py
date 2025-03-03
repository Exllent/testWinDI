import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"


def setup_logger():
    inner_logger = logging.getLogger("app")
    inner_logger.setLevel(LOG_LEVEL)

    root_dir = Path(os.path.abspath(__file__)).parent.parent
    full_path = os.path.join(root_dir, "app.log")

    file_handler = RotatingFileHandler(full_path, maxBytes=10 ** 6, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    inner_logger.addHandler(file_handler)
    return inner_logger


logger = setup_logger()
