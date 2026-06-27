from communication import CommunicationClient
from config import Config
from logger import AgentLogger


class CommandService:

    def __init__(self, action_manager):
        self.config = Config()
        self.client = CommunicationClient()

        self.action_manager = action_manager
        self.logger = AgentLogger().get_logger()


    def poll(self):
        agent_id = self.config.get(
            "agent",
            "id"
        )

        endpoint = self.config.get(
            "server",
            "api",
            "commands"
        )

        endpoint = endpoint.replace(
            "{agent_id}",
            agent_id
        )


        response = self.client.get(endpoint)
        if response is None:
            return

        commands = response.json()

        for command in commands:
            result = self.action_manager.execute(
                command["action"],
                command["payload"]
            )

            print(result)

        