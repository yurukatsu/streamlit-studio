from components import HomePage, LoginForm
from settings import SessionStateManager, Settings


def app():
    Settings.initialize()
    print(Settings.debug)

    if Settings.debug:
        SessionStateManager.set("authenticated", True)

    if SessionStateManager.get("authenticated") is not True:
        LoginForm.render()
    else:
        HomePage.render()


if __name__ == "__main__":
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    app()
