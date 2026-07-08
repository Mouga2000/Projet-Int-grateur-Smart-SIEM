import shutil
import subprocess
import sys
import ctypes
import yaml
from pathlib import Path
from tkinter import messagebox


NOM_SERVICE = "SmartSIEMAgent"
DOSSIER_INSTALL = Path(r"C:\Program Files\SmartSIEM")
CHEMIN_EXEC = DOSSIER_INSTALL / "smart-siem-agent.exe"
CHEMIN_NSSM = DOSSIER_INSTALL / "nssm.exe"



def elever_privileges() -> None:
    """Relance le script avec élévation UAC (équivalent Windows de pkexec)."""
    parametres = " ".join(f'"{arg}"' for arg in sys.argv)
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, parametres, None, 1
    )
    sys.exit(0)


def get_resource_path(relative_path: str) -> Path:
    if getattr(sys, "_MEIPASS", None):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path


def service_existe() -> bool:
    """Vérifie si le service Windows est déjà enregistré."""
    resultat = subprocess.run(
        ["sc", "query", NOM_SERVICE],
        capture_output=True,
        text=True,
    )
    return resultat.returncode == 0


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




def installer_agent_systeme(ip_serveur: str) -> None:
    """Gère toute la configuration Windows automatiquement lors du clic sur le bouton."""
    try:
        # Enregistrer l'IP du serveur choisie par l'utilisateur
        enregistrer_ip_serveur(protocole, hote, port)

        # Copier le binaire actuel et nssm.exe vers le dossier d'installation
        DOSSIER_INSTALL.mkdir(parents=True, exist_ok=True)
        shutil.copy2(sys.argv[0], CHEMIN_EXEC)

        nssm_source = get_resource_path("nssm.exe")
        if nssm_source.exists() and not CHEMIN_NSSM.exists():
            shutil.copy2(nssm_source, CHEMIN_NSSM)

        if not CHEMIN_NSSM.exists():
            raise FileNotFoundError("nssm.exe introuvable : il doit être livré avec l'installateur.")

        # Créer le service Windows via NSSM
        subprocess.run(
            [str(CHEMIN_NSSM), "install", NOM_SERVICE, str(CHEMIN_EXEC)],
            check=True,
        )
        subprocess.run(
            [str(CHEMIN_NSSM), "set", NOM_SERVICE, "AppDirectory", str(DOSSIER_INSTALL)],
            check=True,
        )
        subprocess.run(
            [str(CHEMIN_NSSM), "set", NOM_SERVICE, "DisplayName", "Agent Smart SIEM Integrateur"],
            check=True,
        )
        subprocess.run(
            [str(CHEMIN_NSSM), "set", NOM_SERVICE, "Start", "SERVICE_AUTO_START"],
            check=True,
        )
        subprocess.run(
            [str(CHEMIN_NSSM), "set", NOM_SERVICE, "AppExit", "Default", "Restart"],
            check=True,
        )
        subprocess.run(
            [str(CHEMIN_NSSM), "set", NOM_SERVICE, "AppRestartDelay", "5000"],
            check=True,
        )

        # 4. Démarrer le service
        subprocess.run(["sc", "start", NOM_SERVICE], check=True)

        messagebox.showinfo("Succès", "L'agent SIEM a été installé et démarré avec succès en arrière-plan !")
        sys.exit(0)
    except Exception as e:
        messagebox.showerror("Erreur", f"L'installation a échoué : {str(e)}")





