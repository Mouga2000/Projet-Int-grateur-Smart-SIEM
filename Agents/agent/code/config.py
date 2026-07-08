"""
Configuration Manager

Charge le fichier YAML de configuration.
"""

from pathlib import Path
import yaml
import os
import sys

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class Config:

    def __init__(self):
        chemin_texte = get_resource_path(os.path.join("config", "agent.yml"))
        self.path = Path(chemin_texte) 
        
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


