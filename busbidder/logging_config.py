import logging
from pathlib import Path


LOG_FILE = Path(__file__).resolve().parent.parent / "busbidder.log"


def configure_logging():
    """ Set up the shared log file for the CLI and GUI """

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        encoding="utf-8",
    )