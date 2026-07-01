from abc import ABC, abstractmethod
from actions.result import ActionResult


class BaseAction(ABC):

    name = ""

    @abstractmethod
    def execute(self, parameters:dict)->ActionResult:
        pass