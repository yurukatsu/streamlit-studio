from components import HomePage
from settings import Settings


def app():
    Settings.initialize()
    HomePage.render()


if __name__ == "__main__":
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    app()
