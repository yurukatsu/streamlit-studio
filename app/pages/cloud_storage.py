from components import CloudStoragePage, LoginForm, NavigationBar
from settings import SessionStateManager, Settings


def app():
    Settings.initialize()
    NavigationBar.render()

    if Settings.debug:
        SessionStateManager.set("authenticated", True)

    if SessionStateManager.get("authenticated") is not True:
        LoginForm.render()
    else:
        CloudStoragePage.render()


if __name__ == "__main__":
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    app()
