"""
Registre des actions disponibles.
"""


class ActionRegistry:

    def __init__(self):
        self.actions = {}


    def register(self, action):
        self.actions[action.name] = action


    def get(self, name):
        return self.actions.get(name)


    def all(self):
        return self.actions


    