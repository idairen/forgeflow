"""ForgeFlow logging setup."""
import copy
import logging
import os
import sys
import pathlib as _pathlib


def _init():
    logger = logging.getLogger("forgeflow")
    logger.setLevel(logging.DEBUG)

    class ColorFormatter(logging.Formatter):
        COLORS = {
            logging.DEBUG:    "\033[90m",
            logging.INFO:     "\033[32m",
            logging.WARNING:  "\033[93m",
            logging.ERROR:     "\033[91m",
            logging.CRITICAL: "\033[97;41m",
           }
        RESET = "\033[0m"

        def format(self, record):
            record = copy.copy(record)
            color = self.COLORS.get(record.levelno, "")
            msg = record.getMessage()
            record.msg = f"{color}{msg}{self.RESET}"
            record.args = ()
            return super().format(record)

    fmt = ColorFormatter("%(asctime)s [%(levelname)s] %(message)s",
                         datefmt="%H:%M:%S")
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(fmt)
    if not logger.handlers:
        logger.addHandler(ch)
        log_dir = os.environ.get("FORGEFLOW_LOG_DIR")
        if log_dir:
            try:
                path = _pathlib.Path(log_dir).expanduser()
                path.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(
                    path / "forgeflow.log", encoding="utf-8"
                )
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                ))
                logger.addHandler(file_handler)
            except OSError as error:
                logger.warning("Unable to initialize file logging: %s", error)
    return logger


def get_logger():
    """Return the singleton forgeflow logger."""
    logger = logging.getLogger("forgeflow")
    if not logger.handlers:
        _init()
    return logger
