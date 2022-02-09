'''Menu abstract class'''

from pyrpg.core.states.state import State
from abc import ABC, abstractmethod

class Menu(ABC):

    @abstractmethod
    def show(self) -> None:
        pass

    @abstractmethod
    def hide(self) -> None:
        pass

    @abstractmethod
    def run(self) -> State:
        pass
