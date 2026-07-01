"""
Gestion des processus.
"""

import psutil

from actions.base_action import BaseAction
from actions.result import ActionResult


class ProcessAction(BaseAction):
    name = "process"

    def execute(self, parameters):

        operation = parameters.get("operation")

        try:

            if operation == "kill":
                return self.kill(parameters)

            elif operation == "kill_by_name":
                return self.kill_by_name(parameters)

            elif operation == "list":
                return self.list_processes()

            elif operation == "info":
                return self.info(parameters)

            return ActionResult(
                success=False,
                error="Opération inconnue."
            )

        except Exception as e:

            return ActionResult(
                success=False,
                error=str(e)
            )


    def kill(self, parameters):

        pid = parameters.get("pid")

        process = psutil.Process(pid)

        process.kill()

        return ActionResult(

            success=True,

            message=f"Processus {pid} arrêté."
        )


    def kill_by_name(self, parameters):
        name = parameters.get("name")
        count = 0

        for process in psutil.process_iter(["pid", "name"]):
            if process.info["name"] == name:
                process.kill()
                count += 1

        return ActionResult(
            success=True,
            message=f"{count} processus arrêtés."
        )



    def list_processes(self):
        data = []

        for process in psutil.process_iter( ["pid", "name", "username", "cpu_percent"]):
            data.append(process.info)

        return ActionResult(
            success=True,
            data=data,
            message=f"{len(data)} processus."
        )


    def info(self, parameters):
        pid = parameters.get("pid")
        process = psutil.Process(pid)

        return ActionResult(
            success=True,
            data={

                "pid": process.pid,

                "name": process.name(),

                "exe": process.exe(),

                "status": process.status(),

                "cpu": process.cpu_percent(),

                "memory": process.memory_percent()
            }
        )




