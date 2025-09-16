from abc import ABC, abstractmethod


class BaseComponent(ABC):
    name: str = None

    @classmethod
    @abstractmethod
    def render(cls):
        """
        Render the component.
        """
        pass
