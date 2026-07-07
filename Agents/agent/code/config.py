"""
Configuration Manager

Charge le fichier YAML de configuration.

"""

from pathlib import Path
import yaml


def get_resource_path(relative_path: str) -> Path:
    if getattr(sys, "_MEIPASS", None):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent.parent

    return base_path / relative_path



class Config:

    def __init__(self, path: str = "config/agent.yml"):
        self.path = get_resource_path(path)
        self.data = self.load()



    def load(self) -> dict:

        if not self.path.exists():
            raise FileNotFoundError(
                f"Configuration introuvable : {self.path}"
            )

        with open(self.path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)



    def get(self, *keys):
        value = self.data

        for key in keys:
            value = value[key]

        return value



    def reload(self):
        self.data = self.load()


