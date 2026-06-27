from actions.terminate_process import TerminateProcessAction


class ActionManager:

    def __init__(self):
        self.actions = {}
        self.register= TerminateProcessAction()


    def register(self, action):
        self.actions[ action.action_name] = action


    def execute( self, action_name, payload):
        action = self.actions.get( action_name)

        if action is None:
            return {
                "success": False,
                "message": "Action inconnue"
            }

        return action.execute(
            payload
        )



