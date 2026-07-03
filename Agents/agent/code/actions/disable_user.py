"""
Action SOAR : Désactiver un compte utilisateur local.

Linux  : usermod --lock {username} + chage -E 0 {username}
Windows: net user {username} /active:no
"""

import platform
import subprocess

from code.actions.base_action import BaseAction
from code.actions.result import ActionResult


class DisableUserAction(BaseAction):

    name = "disable_user"

    def execute(self, parameters: dict) -> ActionResult:

        if not parameters:
            return ActionResult(
                success=False,
                error="Aucun paramètre reçu."
            )

        # Si un step du playbook est directement passé
        if "params" in parameters:
            parameters = parameters["params"]

        username = parameters.get("username")
        reason = parameters.get(
            "reason",
            "Désactivation SOAR automatique"
        )

        if not username:
            return ActionResult(
                success=False,
                error="Paramètre 'username' manquant."
            )

        try:

            system = platform.system().lower()

            if system == "windows":
                return self._windows(username, reason)

            if system == "linux":
                return self._linux(username, reason)

            return ActionResult(
                success=False,
                error=f"Système '{system}' non supporté."
            )

        except subprocess.TimeoutExpired:
            return ActionResult(
                success=False,
                error="Temps d'exécution dépassé."
            )

        except Exception as e:
            return ActionResult(
                success=False,
                error=str(e)
            )


    def _linux(self, username: str, reason: str) -> ActionResult:

        # Vérifie si l'utilisateur existe
        check = subprocess.run(
            ["id", username],
            capture_output=True,
            text=True
        )

        if check.returncode != 0:
            return ActionResult(
                success=False,
                error=f"L'utilisateur '{username}' est introuvable."
            )

        # Verrouillage du compte
        r1 = subprocess.run(
            [
                "usermod",
                "--lock",
                username
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if r1.returncode != 0:
            return ActionResult(
                success=False,
                error=r1.stderr.strip()
            )

        # Expiration immédiate
        r2 = subprocess.run(
            [
                "chage",
                "-E",
                "0",
                username
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if r2.returncode != 0:
            return ActionResult(
                success=False,
                error=r2.stderr.strip()
            )

        return ActionResult(
            success=True,
            message=f"Compte '{username}' désactivé. ({reason})"
        )


    def _windows(self, username: str, reason: str) -> ActionResult:

        # Vérifie si le compte existe
        check = subprocess.run(
            [
                "net",
                "user",
                username
            ],
            capture_output=True,
            text=True
        )

        if check.returncode != 0:
            return ActionResult(
                success=False,
                error=f"L'utilisateur '{username}' est introuvable."
            )

        result = subprocess.run(
            [
                "net",
                "user",
                username,
                "/active:no"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return ActionResult(
                success=False,
                error=result.stderr.strip()
            )

        return ActionResult(
            success=True,
            message=f"Compte '{username}' désactivé. ({reason})"
        )





        