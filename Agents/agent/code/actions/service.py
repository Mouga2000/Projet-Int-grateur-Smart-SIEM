"""
Action de gestion des services.
"""

import os
import platform
import subprocess

from actions.base_action import BaseAction
from actions.result import ActionResult


class ServiceAction(BaseAction):
    name = "service"



    def execute(self, parameters):
        try:
            service = parameters.get("service")
            operation = parameters.get("operation")

            if not service:
                return ActionResult(success=False, error="Nom du service manquant.")

            system = platform.system().lower()

            if system == "windows":
                return self._windows(service, operation)

            elif system == "linux":
                return self._linux(service, operation)

            return ActionResult(success=False, error=f"Système {system} non supporté.")

        except Exception as e:
            return ActionResult(success=False, error=str(e))




    def _windows(self, service, operation):
        commands = {
            "start": ["sc", "start", service],
            "stop": ["sc", "stop", service],

            "restart": [
                "powershell",
                "-Command",
                f"Restart-Service -Name '{service}' -Force"
            ],

            "status": ["sc", "query", service]
        }

        if operation not in commands:

            return ActionResult(
                success=False,
                error="Opération inconnue."
            )

        result = subprocess.run(
            commands[operation],
            capture_output=True,
            text=True
        )

        return ActionResult(
            success=result.returncode == 0,
            message=result.stdout,
            error=result.stderr
        )



    def _linux(self, service, operation):
        commands = {
            "start": ["systemctl", "start", service],
            "stop": ["systemctl", "stop", service],
            "restart": ["systemctl", "restart", service],
            "status": ["systemctl", "status", service]
        }

        if operation not in commands:
            return ActionResult(success=False, error="Opération inconnue.")

        result = subprocess.run(
            commands[operation],
            capture_output=True,
            text=True
        )

        return ActionResult(
            success=result.returncode == 0,
            message=result.stdout,
            error=result.stderr
        )


        