from components import HomePage


def app():
    HomePage.render()


if __name__ == "__main__":
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    app()
