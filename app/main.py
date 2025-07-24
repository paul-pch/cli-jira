import logging
from logging import getLogger

import typer

logger = getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = typer.Typer()


@app.command()
def hello(name: str = "World") -> None:
    """Print a greeting message."""
    message = f"Hello {name}! Welcome to your Python CLI application."
    logger.info(message)


if __name__ == "__main__":
    app()
