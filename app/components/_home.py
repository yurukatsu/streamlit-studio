from ._base import BaseComponent
from ._navbar import NavigationBar


class HomePage(BaseComponent):
    name = "home page"

    @classmethod
    def render(cls):
        NavigationBar.render()
