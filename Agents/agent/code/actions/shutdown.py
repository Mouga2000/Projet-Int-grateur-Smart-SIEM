import os
import platform

from actions.base_action import BaseAction
from actions.result import ActionResult


class ShutdownAction(BaseAction):
    name = "shutdown"

    def execute(self, parameters):

        try:
            delay = parameters.get("delay", 0)

            system = platform.system().lower()

            if system == "windows":
                os.system(f"shutdown /s /t {delay}")
            elif system == "linux":
                if delay == 0:
                    os.system("shutdown -h now")
                else:
                    os.system(f"shutdown -h +{delay}")

            else:
                return ActionResult(success=False, error=f"Système '{system}' non supporté.")

            return ActionResult( success=True, message="Arrêt demandé.")

        except Exception as e:
            return ActionResult(success=False, error=str(e))


