"""
Action SOAR : Isoler complètement un hôte du réseau.

Linux  : iptables
Windows: netsh advfirewall

Le serveur SIEM reste accessible afin que l'agent continue
à communiquer.
"""

import platform
import subprocess

from code.actions.base_action import BaseAction
from code.actions.result import ActionResult


class IsolateHostAction(BaseAction):

    name = "isolate_host"

    def execute(self, parameters: dict) -> ActionResult:

        if not parameters:
            return ActionResult(
                success=False,
                error="Aucun paramètre reçu."
            )

        # Compatible avec les playbooks
        if "params" in parameters:
            parameters = parameters["params"]

        siem_ip = parameters.get("siem_ip")
        comment = parameters.get(
            "comment",
            "Isolation SOAR automatique"
        )

        if not siem_ip:
            return ActionResult(
                success=False,
                error="Paramètre 'siem_ip' manquant."
            )

        try:

            system = platform.system().lower()

            if system == "windows":
                return self._windows(siem_ip, comment)

            if system == "linux":
                return self._linux(siem_ip, comment)

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


    def _linux(self, siem_ip: str, comment: str) -> ActionResult:

        commands = [

            ["iptables", "-P", "INPUT", "DROP"],
            ["iptables", "-P", "OUTPUT", "DROP"],

            ["iptables", "-A", "INPUT", "-s", siem_ip, "-j", "ACCEPT"],
            ["iptables", "-A", "OUTPUT", "-d", siem_ip, "-j", "ACCEPT"],

        ]

        for cmd in commands:

            result = subprocess.run(
                cmd,
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
            message=(
                f"Hôte isolé. "
                f"Communication avec le SIEM ({siem_ip}) conservée. "
                f"({comment})"
            )
        )


    def _windows(self, siem_ip: str, comment: str) -> ActionResult:

        commands = [

            [
                "netsh", "advfirewall", "firewall", "add", "rule",
                "name=SIEM_Block_IN",
                "dir=in",
                "action=block"
            ],

            [
                "netsh", "advfirewall", "firewall", "add", "rule",
                "name=SIEM_Block_OUT",
                "dir=out",
                "action=block"
            ],

            [
                "netsh", "advfirewall", "firewall", "add", "rule",
                "name=SIEM_Allow_IN",
                "dir=in",
                "action=allow",
                f"remoteip={siem_ip}"
            ],

            [
                "netsh", "advfirewall", "firewall", "add", "rule",
                "name=SIEM_Allow_OUT",
                "dir=out",
                "action=allow",
                f"remoteip={siem_ip}"
            ]

        ]

        for cmd in commands:

            result = subprocess.run(
                cmd,
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
            message=(
                f"Hôte isolé. "
                f"Communication avec le SIEM ({siem_ip}) conservée. "
                f"({comment})"
            )
        )




        