import subprocess


class ScriptAction(BaseAction):

    def execute(self, command):

        script = command.get("script")

        if script == "block_ip":
            return self.block_ip(command)

        elif script == "unblock_ip":
            return self.unblock_ip(command)

        elif script == "disable_user":
            return self.disable_user(command)

        elif script == "enable_user":
            return self.enable_user(command)

        elif script == "isolate_host":
            return self.isolate_host(command)

        elif script == "collect_forensic":
            return self.collect_forensic(command)

        elif script == "execute_playbook":
            return self.execute_playbook(command)

        else:
            return ActionResult(
                False,
                f"Script inconnu : {script}"
            )
        


    def block_ip(self, command):
        ip = command.get("ip")

        if not ip:
            return ActionResult(False, "Adresse IP absente")

        try:
            if platform.system() == "Windows":
                subprocess.run(
                    [
                        "netsh",
                        "advfirewall",
                        "firewall",
                        "add",
                        "rule",
                        f"name=SIEM_BLOCK_{ip}",
                        "dir=in",
                        "action=block",
                        f"remoteip={ip}"
                    ],
                    check=True
                )

            else:
                subprocess.run(
                    [
                        "iptables",
                        "-A",
                        "INPUT",
                        "-s",
                        ip,
                        "-j",
                        "DROP"
                    ],
                    check=True
                )

            return ActionResult(True, f"{ip} bloquée")

        except Exception as e:
            return ActionResult(False, str(e))



    def unblock_ip(self, command):
        ip = command.get("ip")

        if not ip:
            return ActionResult(False, "Adresse IP absente")

        try:
            if platform.system() == "Windows":
                subprocess.run(
                    [
                        "netsh",
                        "advfirewall",
                        "firewall",
                        "delete",
                        "rule",
                        f"name=SIEM_BLOCK_{ip}"
                    ],
                    check=True
                )
            else:
                subprocess.run(
                    [
                        "iptables",
                        "-D",
                        "INPUT",
                        "-s",
                        ip,
                        "-j",
                        "DROP"
                    ],
                    check=True
                )

            return ActionResult(True, f"{ip} débloquée")

        except Exception as e:
            return ActionResult(False, str(e))



    def disable_user(self, command):
        username = command.get("username")

        if not username:
            return ActionResult(False, "Utilisateur absent")

        try:
            if platform.system() == "Windows":
                subprocess.run(
                    [
                        "net",
                        "user",
                        username,
                        "/active:no"
                    ],
                    check=True
                )
            else:
                subprocess.run(
                    [
                        "passwd",
                        "-l",
                        username
                    ],
                    check=True
                )

            return ActionResult(True, f"{username} désactivé")

        except Exception as e:
            return ActionResult(False, str(e))




    def enable_user(self, command):
        username = command.get("username")

        if not username:
            return ActionResult(False, "Utilisateur absent")

        try:
            if platform.system() == "Windows":
                subprocess.run(
                    [
                        "net",
                        "user",
                        username,
                        "/active:yes"
                    ],
                    check=True
                )
            else:
                subprocess.run(
                    [
                        "passwd",
                        "-u",
                        username
                    ],
                    check=True
                )

            return ActionResult(True, f"{username} activé")

        except Exception as e:
            return ActionResult(False, str(e))



    def isolate_host(self, command):
        pass

    def collect_forensic(self, command):
        pass
    
    def execute_playbook(self, command):
        pass




