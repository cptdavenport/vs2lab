import logging

from rich.logging import RichHandler


def setup_logging(log_level: str = "NOTSET"):
    log_format = "[%(name)s] %(message)s"
    rich_handler = RichHandler(show_path=False)
    logging.basicConfig(
        level=log_level, format=log_format, datefmt="[%X]", handlers=[rich_handler]
    )