"""
Action SOAR : Bloquer une adresse IP via le pare-feu système.

Linux  : iptables -A INPUT -s {ip} -j DROP
Windows: netsh advfirewall firewall add rule ...
"""

import platform
import subprocess

from code.actions.base_action import BaseAction
from code.actions.result import ActionResult


class BlockIPAction(BaseAction):
    name = "block_ip"

    def execute(self, parameters: dict) -> ActionResult:
        if not parameters:
            return ActionResult(success=False, error="Aucun paramètre reçu.")

        # Cas d'un playbook complet
        if "params" in parameters:
            parameters = parameters["params"]

        ip = parameters.get("ip")
        comment = parameters.get("comment", "Blocage SOAR automatique")
        

        if not ip:
            return ActionResult(success=False, error="Paramètre 'ip' manquant.")

        try:
            system = platform.system().lower()

            if system == "windows":
                print(f"Ip à bloquer : {ip}")
                return self._windows(ip, comment)

            if system == "linux":
                return self._linux(ip, comment)

            return ActionResult(success=False, error=f"Système '{system}' non supporté.")

        except subprocess.TimeoutExpired:
            return ActionResult(
                success=False,
                error="Temps d'exécution dépassé."
            )

        except Exception as e:
            return ActionResult(success=False, error=str(e))





    def _linux(self, ip: str, comment: str) -> ActionResult:
        result = subprocess.run(
            ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return ActionResult(
                success=True,
                message=f"IP {ip} bloquée via iptables. ({comment})"
            )

        return ActionResult(
            success=False,
            error=f"iptables a échoué : {result.stderr.strip()}"
        )


    def _windows(self, ip: str, comment: str) -> ActionResult:
        rule_name = f"SIEM_Block_{ip.replace('.', '_').replace(':', '_')}"

        result = subprocess.run(
            [
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name={rule_name}",
                "dir=in",
                "action=block",
                f"remoteip={ip}"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return ActionResult(
                success=True,
                message=f"IP {ip} bloquée via netsh (règle : {rule_name}). ({comment})"
            )

        return ActionResult(
            success=False,
            error=f"netsh a échoué : {result.stderr.strip()}"
        )



