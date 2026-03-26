import logging
import logging.config
import os
from pathlib import Path


def get_logging_config():
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "logs/app.log")

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            },
            "json": {
                "format": (
                    '{"timestamp":"%(asctime)s",'
                    '"level":"%(levelname)s",'
                    '"logger":"%(name)s",'
                    '"message":"%(message)s"}'
                )
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": log_level,
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": log_file,
                "formatter": "json",
                "level": log_level,
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": log_level,
        },
    }


def setup_logging():
    log_file = os.getenv("LOG_FILE", "logs/app.log")

    # Auto create logs folder
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig(get_logging_config())
