"""
Communication avec le serveur Smart SIEM.
"""

import requests

from code.config import Config
from code.logger import AgentLogger


class CommunicationClient:

    def __init__(self):
        self.config = Config()

        self.logger = AgentLogger().get_logger()

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



    def _headers(self):
        headers = {
            "Content-Type": "application/json"
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers


    def post(self, payload):

        endpoint = self.config.get(
            "server",
            "api",
            "logs"
        )

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

            self.logger.info(
                f"POST {endpoint} -> {response.status_code}"
            )

            return True

        except requests.exceptions.RequestException as e:
            self.logger.error(str(e))
            return False




    def get(self, endpoint):

        url = self.base_url + endpoint

        try:
            response = requests.get(
                url=url,
                headers=self._headers(),
                timeout=self.timeout,
                verify=self.verify_ssl
            )

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            self.logger.error(str(e))
            return None


    def ping(self):

        endpoint = self.config.get(
            "server",
            "api",
            "ping"
        )

        try:
            response = requests.get(
                self.base_url + endpoint,
                headers=self._headers(),
                timeout=self.timeout,
                verify=self.verify_ssl
            )

            return response.status_code == 200

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ping failed: {e}")
            return False

