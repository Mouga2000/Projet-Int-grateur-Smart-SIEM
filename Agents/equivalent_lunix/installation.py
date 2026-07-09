
import os
import sys
from pathlib import Path
from tkinter import messagebox
import yaml



# Si le programme est figé (.exe/PyInstaller), la racine est sys._MEIPASS
if getattr(sys, "frozen", False):
    sys.path.insert(0, sys._MEIPASS)

CHEMIN_SERVICE = "/etc/systemd/system/smart-siem.service"
CHEMIN_EXEC = "/usr/local/bin/smart-siem-agent"


# --------------------------------------------------------------------------
# Partie "assistant d'installation" (ex build_gui.py)
# --------------------------------------------------------------------------



def est_admin() -> bool:
    """Vérifie si le script est exécuté avec les privilèges d'administrateur."""
    return os.getuid() == 0





def get_resource_path(relative_path: str) -> Path:
    if getattr(sys, "_MEIPASS", None):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path



def enregistrer_ip_serveur(protocole: str, hote: str, port: str) -> None:
    """
    Écrit protocole / hôte / port du serveur SIEM dans config/agent.yml,
    pour que Config().get("server", "protocol"|"host"|"port") fonctionne
    partout ailleurs dans l'agent. Fusionne avec le contenu existant.
    """
    chemin_config = get_resource_path("config/agent.yml")
    chemin_config.parent.mkdir(parents=True, exist_ok=True)
 
    donnees = {}
    if chemin_config.exists():
        with open(chemin_config, "r", encoding="utf-8") as f:
            donnees = yaml.safe_load(f) or {}
 
    donnees.setdefault("server", {})
    donnees["server"]["protocol"] = protocole
    donnees["server"]["host"] = hote
    donnees["server"]["port"] = int(port)
 
    with open(chemin_config, "w", encoding="utf-8") as f:
        yaml.safe_dump(donnees, f, allow_unicode=True, sort_keys=False)
 

 

def service_existe() -> bool:
    """Vérifie si le service systemd est déjà installé."""
    return os.path.exists(CHEMIN_SERVICE)






def installer_agent_systeme(protocole: str, hote: str, port: str) -> None:
    """Gère toute la configuration Linux automatiquement lors du clic sur le bouton."""
    try:
        # 1. Enregistrer l'IP du serveur choisie par l'utilisateur
        enregistrer_ip_serveur(protocole, hote, port)

        # 2. Copier le fichier binaire actuel vers son emplacement système définitif
        os.system(f"cp {sys.argv[0]} {CHEMIN_EXEC}")
        os.system(f"chmod +x {CHEMIN_EXEC}")

        # 3. Générer dynamiquement le fichier de service Systemd
        contenu_service = f"""[Unit]
Description=Agent Smart SIEM Integrateur
After=network.target

[Service]
Type=simple
User=root
ExecStart={CHEMIN_EXEC}
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
        with open(CHEMIN_SERVICE, "w") as f:
            f.write(contenu_service)

        # 4. Activer et lancer le service en arrière-plan
        os.system("systemctl daemon-reload")
        os.system("systemctl enable smart-siem.service")
        os.system("systemctl start smart-siem.service")

        messagebox.showinfo(
            "Succès",
            "L'agent SIEM a été installé et démarré avec succès en arrière-plan !",
        )
        sys.exit(0)
    except Exception as e:
        messagebox.showerror("Erreur", f"L'installation a échoué : {str(e)}")

