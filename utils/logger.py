import logging
from logging.config import dictConfig
from pathlib import Path

from utils.config import config

LOGGER_NAME = "bitcoin-fullnode-exporter"

def set_up_logger(
    log_level: str,
    log_path: str | None,
    logger_name: str,
) -> logging.Logger:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": (
                    "[\033[90m%(asctime)s\033[m]"
                    "%(log_color)s |%(log_color)-10s%(levelname)-8s|"
                    "%(reset)s \033[0m%(message)s\033[m"
                ),
                "datefmt": "%H:%M:%S",
                "()": "colorlog.ColoredFormatter",
                "log_colors": {
                    "INFO": "bold_green",
                    "WARNING": "bold_yellow",
                    "ERROR": "bold_red",
                    "CRITICAL": "bold_purple",
                    "DEBUG": "bold_cyan",
                    "TRACE": "bold_light_blue",
                },
            },
            "file": {
                "format": (
                    "[{asctime}] [{levelname}] "
                    "[{name}]: {message} - {filename}"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "style": "{",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": log_level,
            }
        },
        "loggers": {
            logger_name: {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            }
        },
    }

    if log_path:
        log_file = Path(log_path).expanduser()
        log_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        logging_config["handlers"]["file"] = {
            "class": "logging.FileHandler",
            "formatter": "file",
            "filename": str(log_file),
            "level": log_level,
            "encoding": "utf-8",
        }

        logging_config["loggers"][logger_name][
            "handlers"
        ].append("file")

    dictConfig(logging_config)

    return logging.getLogger(logger_name)


logger = set_up_logger(
    log_level=config.app_log_level,
    log_path=config.app_log_path,
    logger_name=LOGGER_NAME,
)