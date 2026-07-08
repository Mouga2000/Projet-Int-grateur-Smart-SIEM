"""
Point d'entrée unique du Smart Agent - Version Windows.

Comportement :
  - Si le service Windows n'existe pas encore -> ouverture de l'assistant
    graphique d'installation (saisie IP serveur, copie du binaire,
    création + démarrage du service Windows via NSSM).
  - Si le service existe déjà -> démarrage direct de la boucle SmartAgent
    (c'est ce que le service exécute à chaque démarrage de la machine).

Prérequis d'empaquetage :
  - nssm.exe doit être livré à côté de l'exécutable (ou dans les ressources
    PyInstaller) pour permettre la création du service Windows.
"""


import sys
import ctypes

from code.interface import lancer_assistant_graphique
from code.installation import service_existe, elever_privileges
from code.lancer_agent import lancer_smart_agent


# Si le programme est figé (.exe/PyInstaller), la racine est sys._MEIPASS
if getattr(sys, "frozen", False):
    sys.path.insert(0, sys._MEIPASS)




# --------------------------------------------------------------------------
# Partie "assistant d'installation"
# --------------------------------------------------------------------------

def est_admin() -> bool:
    """Vérifie si le script est exécuté avec les privilèges administrateur."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False





# --------------------------------------------------------------------------
# Point d'entrée principal
# --------------------------------------------------------------------------

if __name__ == "__main__":
    if not service_existe():
        # Premier lancement sur le poste : on ouvre l'assistant graphique.
        if not est_admin():
            elever_privileges()
        lancer_assistant_graphique()
    else:
        # Déjà installé : on démarre directement la boucle SIEM.
        lancer_smart_agent()
       

