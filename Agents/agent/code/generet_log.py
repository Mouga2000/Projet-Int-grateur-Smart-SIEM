import random
import time
from datetime import datetime

LOG_FILE = "D:\\Promo X2028\\X3\\Projet Intégrateur\\Realisation\\Projet-Int-grateur-Smart-SIEM\\Agents\\agent\\logs\\test.log"

LEVELS = [
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL"
]

EVENTS = [

    "Utilisateur admin connecté",

    "Tentative SSH échouée",

    "Connexion RDP",

    "Service Apache arrêté",

    "Service Apache démarré",

    "Processus python.exe lancé",

    "Processus powershell.exe lancé",

    "Connexion VPN établie",

    "Port 22 ouvert",

    "Port 3389 ouvert",

    "Adresse IP bloquée",

    "Fichier supprimé",

    "Fichier modifié",

    "Téléchargement terminé",

    "Nouvelle session utilisateur",

    "Échec d'authentification",

    "Accès refusé",

    "Firewall activé",

    "Firewall désactivé",

    "Connexion à la base de données"
]


print("Génération des logs...")

while True:

    level = random.choice(LEVELS)

    event = random.choice(EVENTS)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"{now} | {level} | {event}"

    with open(LOG_FILE, "a", encoding="utf8") as file:

        file.write(line + "\n")

    print(line)

    time.sleep(random.randint(2,5))