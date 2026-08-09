import logging
import sys
import os
from config import settings


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    # Avoid duplicate logs if re-imported
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)

    os.makedirs("logs", exist_ok=True)
    file_handler = logging.FileHandler(settings.log_file, encoding="utf-8")

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
