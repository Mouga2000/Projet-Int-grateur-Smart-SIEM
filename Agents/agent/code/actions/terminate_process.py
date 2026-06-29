import psutil
from actions.base_action import BaseAction


class TerminateProcessAction(BaseAction):

    @property
    def action_name(self):
        return "terminate_process"


    def execute(self, payload):

        pid = payload.get("pid")

        if pid is None:
            return {
                "success": False,
                "message": "PID manquant"
            }

        try:

            process = psutil.Process(pid)
            process.terminate()

            return {
                "success": True,
                "message": f"Processus {pid} arrêté"
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }





