"""
Gestionnaire des actions.
"""

from logger import AgentLogger
from actions.registry import ActionRegistry

from actions.shutdown import ShutdownAction
from actions.restart import RestartAction
from actions.service import ServiceAction
from actions.process import ProcessAction
from actions.block_ip import BlockIPAction
from actions.disable_user import DisableUserAction
from actions.isolate_host import IsolateHostAction


class ActionManager:

    def __init__(self):
        self.logger = AgentLogger().get_logger()
        self.registry = ActionRegistry()

        self.register(ShutdownAction())
        self.register (RestartAction ())
        self.register(ServiceAction())
        self.register(ProcessAction())
        self.register(BlockIPAction())
        self.register(DisableUserAction())
        self.register(IsolateHostAction())

        self.block_ip_action = BlockIPAction()
        self.disable_user_action = DisableUserAction()
        self.isolate_host_action = IsolateHostAction()






    def register(self, action):
        self.registry.register(action)


    def execute(self, command):
        action = self.registry.get(command["action"])

        if action is None:
            self.logger.warning(f"Action inconnue : {command['action']}")
            return False

        result = action.execute(command.get("parameters", {}))

        if result.success:
            self.logger.info(result.message)
        else:
            self.logger.error(result.error)

        return result




