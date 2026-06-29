from abc import ABC, abstractmethod


class BaseAction(ABC):

    @property
    @abstractmethod
    def action_name(self):
        pass

    @abstractmethod
    def execute(self, payload):
        pass

    