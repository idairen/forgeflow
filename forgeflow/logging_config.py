"""ForgeFlow logging setup."""
import logging
import os
import sys
import pathlib as _pathlib

# --- Logger singleton ---
FORGEFLOW_LOG_DIR = _pathlib.Path(".forgeflow/logs")


def _init():
    FORGEFLOW_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = str(FORGEFLOW_LOG_DIR / "forgeflow.log")

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
            color = self.COLORS.get(record.levelno, "")
            msg = record.getMessage()
            record.msg = f"{color}{msg}{self.RESET}"
            record.args = ()
            return super().format(record)

    fmt = ColorFormatter("%(asctime)s [%(levelname)s] %(message)s",
                         datefmt="%H:%M:%S")
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(fmt)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
         "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)
    return logger


def get_logger():
    """Return the singleton forgeflow logger."""
    logger = logging.getLogger("forgeflow")
    if not logger.handlers:
        _init()
    return logger
