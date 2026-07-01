"""
Action de redémarrage de la machine.
"""

import os
import platform

from actions.base_action import BaseAction
from actions.result import ActionResult


class RestartAction(BaseAction):
    name = "restart"



    def execute(self, parameters):
        try:
            delay = parameters.get("delay", 0)
            system = platform.system().lower()

            if system == "windows":
                os.system(f"shutdown /r /t {delay}")
            elif system == "linux":
                if delay == 0:
                    os.system("shutdown -r now")
                else:
                    os.system(f"shutdown -r +{delay}")

            else:
                return ActionResult(success=False, error=f"Système '{system}' non supporté.")


            return ActionResult(success=True, message=f"Redémarrage programmé dans {delay} seconde(s).")

        except Exception as e:
            return ActionResult(success=False, error=str(e))


