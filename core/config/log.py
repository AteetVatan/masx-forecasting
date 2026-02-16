import logging
import logging.config
import sys


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "structured": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "structured",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}


def setup_logging(*, level: str = "INFO") -> None:
    LOG_CONFIG["root"]["level"] = level
    logging.config.dictConfig(LOG_CONFIG)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
