"""
Communication avec le serveur Smart SIEM.
"""

from typing import Any
import requests
from config import Config
from logger import AgentLogger


class CommunicationClient:

    def __init__(self):

        self.config = Config()
        agent_logger = AgentLogger()

        self.logger = agent_logger.get_logger()

        server = self.config.get("server")

        self.base_url = (
            f"{server['protocol']}://"
            f"{server['host']}:"
            f"{server['port']}"
        )

        self.timeout = server["timeout"]

        self.verify_ssl = server["verify_ssl"]

        self.token = self.config.get(
            "authentication",
            "token"
        )




    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}

        if self.token:
            headers["Authorization"] = (
                f"Bearer {self.token}"
            )

        return headers



    def post(self, payload: dict) -> bool:
        endpoint = self.config.get("server", "api", "events")
        url = self.base_url + endpoint

        try:
            response = requests.post(
                url=url,
                json=payload,
                headers=self._headers(),
                timeout=self.timeout,
                verify=self.verify_ssl
            )

            response.raise_for_status()

            self.logger.info( f"POST {endpoint} -> {response.status_code}")

            return True

        except requests.exceptions.RequestException as e:
            self.logger.error(str(e))

            return False




    def ping(self):
        header = self.config.get("server", "api", "ping")
        try:
            response = requests.get(
                self.base_url +
                header,
                timeout=3
            )
            return response.status_code == 200

        except:
            return False


