"""
Collecteur des services système.
"""

import psutil
import platform
import subprocess
from config import Config
from logger import AgentLogger
from models.event import Event


class ServicesCollector:

    def __init__(self):
        self.config = Config()
        log = AgentLogger()

        self.logger = log.get_logger()
        self.previous_states = {}
        self.system = platform.system()



    def collect(self):

        if self.system == "Windows":
            print("*"*50)
            print("windows"*2)
            return self.collect_windows_services()

        elif self.system == "Linux":
            print("*"*50)
            print("lunix"*2)
            return self.collect_linux_services()

        return []
    


    def get_critical_services(self):

        if self.system == "Windows":

            return self.config.get(
                "services",
                "critical",
                "windows"
            )

        elif self.system == "Linux":

            return self.config.get(
                "services",
                "critical",
                "linux"
            )

        return []


    def detect_change( self, service_name, current_status):

        old_status = self.previous_states.get(service_name)

        self.previous_states[service_name] = current_status

        if old_status is None:
            return None

        if old_status != current_status:
            return {
                "old": old_status,
                "new": current_status
            }

        return None



    def collect_windows_services(self) -> list[Event]:
        events = []

        max_services = self.config.get(
            "services",
            "max_services"
        )
        
        critical_services = self.get_critical_services()
        monitor_only = self.config.get(
            "services",
            "monitor_only_critical"
        )


        try:
            services = list(psutil.win_service_iter())

        except Exception as e:
            self.logger.error(f"Impossible de récupérer les services : {e}")
            return events

        

        for service in services[:max_services]:
            try:
                
                info = service.as_dict()
                
                if monitor_only and info["name"] not in critical_services:
                    continue


                event = Event()

                event.agent_id = self.config.get(
                    "agent",
                    "id"
                )

                event.collector = "ServicesCollector"

                event.event_type = "service_status"

                event.message = (
                    f"Service {info['name']} "
                    f"({info['status']})"
                )

                event.data = {

                    "name": info["name"],

                    "display_name": info["display_name"],

                    "status": info["status"],

                    "start_type": info["start_type"],

                    "username": info["username"]

                }


                change = self.detect_change(
                    info["name"],
                    info["status"]
                )

                
                print("1111111")


                if change:
                    event.event_type = ("service_state_changed")

                    event.message = (
                        f"{info['name']} : "
                        f"{change['old']} -> "
                        f"{change['new']}"
                    )

                    event.data["old_status"] = (change["old"])
                    event.data["new_status"] = (change["new"])

                if info["name"] in critical_services:
                    event.data["critical"] = True

                events.append(event)
                

                

            except Exception as e:
                self.logger.error(e)
                continue

        self.logger.info(f"{len(events)} services collectés")

        return events




    def collect_linux_services(self):
        events = []
        monitor_only = self.config.get(
            "services",
            "monitor_only_critical"
        )

        try:
            result = subprocess.run(
                [
                    "systemctl",
                    "list-units",
                    "--type=service",
                    "--all",
                    "--no-pager",
                    "--no-legend"
                ],

                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                self.logger.error(
                    result.stderr
                )
                return []


            services = result.stdout.splitlines()
            critical_services = self.get_critical_services()


            for service_line in services:
                parts = service_line.split()

                if len(parts) < 4:
                    continue

                service_name = parts[0]

                load_state = parts[1]

                active_state = parts[2]

                sub_state = parts[3]

                if monitor_only and service_name not in critical_services:
                    continue

                event = Event()

                event.agent_id = self.config.get(
                    "agent",
                    "id"
                )

                event.collector = "ServicesCollector"

                event.event_type = "service_status"

                event.message = (
                    f"Service {service_name} "
                    f"({active_state})"
                )

                event.data = {
                    "name": service_name,

                    "load_state": load_state,

                    "active_state": active_state,

                    "sub_state": sub_state
                }


                change = self.detect_change(
                    service_name,
                    active_state
                )

                
                if change:
                    event.event_type = ("service_state_changed")

                    event.message = (
                        f"{service_name} : "
                        f"{change['old']} -> "
                        f"{change['new']}"
                    )

                    event.data["old_status"] = (change["old"])
                    event.data["new_status"] = (change["new"])

                if (service_name  in critical_services ):
                    event.data["critical"] = True

                events.append(event)

                

        except Exception as e:
            self.logger.error(f"Erreur Linux Services : {e}")

        return events

