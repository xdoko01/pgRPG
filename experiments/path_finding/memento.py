from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from random import sample
from string import ascii_letters



class PathCalculation:
    """
    The PathCalculation holds some important state that may change over time. It also
    defines a method for saving the state inside a memento and another method
    for restoring the state from it.
    """

    _state = None
    """
    For the sake of simplicity, the PathCalculation's state is stored inside a single
    variable.
    """

    def __init__(self, state: str) -> None:
        self._state = state
        print(f"PathCalculation: My initial state is: {self._state}")

    def do_something(self) -> None:
        """
        The PathCalculation's business logic may affect its internal state.
        Therefore, the client should backup the state before launching methods
        of the business logic via the save() method.
        """

        print("PathCalculation: I'm doing something important.")
        self._state = self._generate_random_string(30)
        print(f"PathCalculation: and my state has changed to: {self._state}")

    @staticmethod
    def _generate_random_string(length: int = 10) -> str:
        return "".join(sample(ascii_letters, length))

    def save(self) -> Memento:
        """
        Saves the current state inside a memento.
        """

        return ConcreteMemento(self._state)

    def restore(self, memento: Memento) -> None:
        """
        Restores the PathCalculation's state from a memento object.
        """

        self._state = memento.get_state()
        print(f"PathCalculation: My state has changed to: {self._state}")


class Memento(ABC):
    """
    The Memento interface provides a way to retrieve the memento's metadata,
    such as creation date or name. However, it doesn't expose the Originator's
    state.
    """

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_date(self) -> str:
        pass


class PathCalcState(Memento):
    def __init__(self, state: str) -> None:
        self._state = state
        self._date = str(datetime.now())[:19]

    def get_state(self) -> str:
        """
        The PathCalculation uses this method when restoring its state.
        """
        return self._state

    def get_name(self) -> str:
        """
        The rest of the methods are used by the Caretaker to display metadata.
        """

        return f"{self._date} / ({self._state[0:9]}...)"

    def get_date(self) -> str:
        return self._date


class PathCalcManager:
    """
    The Caretaker doesn't depend on the Concrete Memento class. Therefore, it
    doesn't have access to the originator's state, stored inside the memento. It
    works with all mementos via the base Memento interface.
    """

    def __init__(self, originator: PathCalculation) -> None:
        self._mementos = []
        self._originator = originator

    def backup(self) -> None:
        print("\nPathCalcManager: Saving PathCalculation's state...")
        self._mementos.append(self._originator.save())

    def undo(self) -> None:
        if not len(self._mementos):
            return

        memento = self._mementos.pop()
        print(f"PathCalcManager: Restoring state to: {memento.get_name()}")
        try:
            self._originator.restore(memento)
        except Exception:
            self.undo()

    def show_history(self) -> None:
        print("Caretaker: Here's the list of mementos:")
        for memento in self._mementos:
            print(memento.get_name())


if __name__ == "__main__":
    path_calculation = PathCalculation("Super-duper-super-puper-super.")
    path_calc_manager = PathCalcManager(path_calculation)

    path_calc_manager.backup()
    path_calculation.do_something()

    path_calc_manager.backup()
    path_calculation.do_something()

    path_calc_manager.backup()
    path_calculation.do_something()

    print()
    path_calc_manager.show_history()

    print("\nClient: Now, let's rollback!\n")
    path_calc_manager.undo()

    print("\nClient: Once more!\n")
    path_calc_manager.undo()