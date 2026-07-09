"""
interface.py

Assistant graphique Tkinter d'installation du Smart Agent.
Ne contient aucune logique système : délègue à installation.installer_agent_systeme().
"""



import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from code.installation import installer_agent_systeme


# ==============================================================
# Palette
# ==============================================================
COLOR_PRIMARY = "#0A2F6F"     # bleu nuit - header
COLOR_SECONDARY = "#1E88E5"   # bleu accent - focus / liens
COLOR_ACCENT = "#b19766"      # doré - accent discret
COLOR_BG = "#F4F7FA"          # fond fenêtre
COLOR_CARD = "#FFFFFF"        # fond carte
COLOR_TEXT = "#1E293B"        # texte principal
COLOR_MUTED = "#5C6773"       # texte secondaire
COLOR_BORDER = "#D9E2EC"
COLOR_INFO_BG = "#EDF5FF"
COLOR_INFO_BORDER = "#C5D9F1"
COLOR_SUCCESS = "#1B7F4C"
COLOR_ERROR = "#C62828"

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SUBTITLE = ("Segoe UI", 9)
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_INPUT = ("Segoe UI", 11)
FONT_BUTTON = ("Segoe UI", 11, "bold")
FONT_SMALL = ("Segoe UI", 9)



def elever_privileges() -> None:
    if getattr(sys, "frozen", False):
        commande_cible = [os.path.abspath(sys.executable)] + sys.argv[1:]
    else:
        commande_cible = ["python3", os.path.abspath(sys.argv[0])] + sys.argv[1:]

    display = os.environ.get("DISPLAY", ":0")
    xauthority = os.environ.get("XAUTHORITY", "")

    arguments_pkexec = ["pkexec", "env", f"DISPLAY={display}"]
    
    if xauthority:
        arguments_pkexec.append(f"XAUTHORITY={xauthority}")
    

    arguments_pkexec.extend(commande_cible)

    os.execv("/usr/bin/pkexec", arguments_pkexec)
    sys.exit(0)



def est_root() -> bool:
    return os.getuid() == 0


def lancer_assistant_graphique() -> None:

    if not est_root():
        elever_privileges()



    fenetre = tk.Tk()
    fenetre.title("Smart SIEM Agent — Assistant d'installation")
    fenetre.geometry("520x700")
    fenetre.minsize(480, 640)
    fenetre.configure(bg=COLOR_BG)

    # Style ttk pour le Combobox (protocole)
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Smart.TCombobox",
        fieldbackground="white",
        background="white",
        foreground=COLOR_TEXT,
        arrowcolor=COLOR_PRIMARY,
        padding=4,
    )

    # ==========================================================
    # Carte centrale (scindée en header coloré + corps blanc)
    # ==========================================================
    outer = tk.Frame(fenetre, bg=COLOR_BG)
    outer.pack(expand=True, fill="both", padx=24, pady=24)

    card = tk.Frame(
        outer,
        bg=COLOR_CARD,
        highlightthickness=1,
        highlightbackground=COLOR_BORDER,
    )
    card.pack(expand=True, fill="both")

    # ---------- Header ----------
    header = tk.Frame(card, bg=COLOR_PRIMARY)
    header.pack(fill="x")

    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        try:
            logo = tk.PhotoImage(file=logo_path)
            logo_label = tk.Label(header, image=logo, bg=COLOR_PRIMARY)
            logo_label.image = logo  # garder une référence
            logo_label.pack(pady=(24, 8))
        except tk.TclError as e:
            print(e)

    tk.Label(
        header,
        text="Smart SIEM Agent",
        bg=COLOR_PRIMARY,
        fg="white",
        font=FONT_TITLE,
    ).pack(pady=(0, 4))

    tk.Label(
        header,
        text="Configuration et installation de l'agent de sécurité",
        bg=COLOR_PRIMARY,
        fg="#C9D8F2",
        font=FONT_SUBTITLE,
    ).pack(pady=(0, 22))

    # ---------- Corps ----------
    body = tk.Frame(card, bg=COLOR_CARD)
    body.pack(expand=True, fill="both", padx=32, pady=24)

    tk.Label(
        body,
        text="CONNEXION AU SERVEUR",
        bg=COLOR_CARD,
        fg=COLOR_MUTED,
        font=("Segoe UI", 9, "bold"),
        anchor="w",
    ).pack(fill="x", pady=(0, 8))

    # Ligne de formulaire : protocole / hôte / port, alignée avec grid()
    frame_formulaire = tk.Frame(body, bg=COLOR_CARD)
    frame_formulaire.pack(fill="x")
    frame_formulaire.columnconfigure(0, weight=0)
    frame_formulaire.columnconfigure(1, weight=1)
    frame_formulaire.columnconfigure(2, weight=0)

    def champ_label(parent, texte):
        tk.Label(
            parent, text=texte, bg=COLOR_CARD, fg=COLOR_TEXT,
            font=FONT_LABEL, anchor="w",
        ).pack(fill="x", pady=(0, 4))

    # Protocole
    col_proto = tk.Frame(frame_formulaire, bg=COLOR_CARD)
    col_proto.grid(row=0, column=0, sticky="ew", padx=(0, 8))
    champ_label(col_proto, "Protocole")
    combo_protocol = ttk.Combobox(
        col_proto, values=["http", "https"], width=7,
        font=FONT_INPUT, state="readonly", style="Smart.TCombobox",
    )
    combo_protocol.set("http")
    combo_protocol.pack(ipady=4, fill="x")

    # Hôte
    col_hote = tk.Frame(frame_formulaire, bg=COLOR_CARD)
    col_hote.grid(row=0, column=1, sticky="ew", padx=8)
    champ_label(col_hote, "Adresse hôte (IP / domaine)")
    champ_hote = tk.Entry(
        col_hote, justify="center", font=FONT_INPUT,
        relief="solid", bd=1, highlightthickness=1,
        highlightbackground=COLOR_BORDER, highlightcolor=COLOR_SECONDARY,
    )
    champ_hote.insert(0, "192.168.1.110")
    champ_hote.pack(ipady=6, fill="x")

    # Port
    col_port = tk.Frame(frame_formulaire, bg=COLOR_CARD)
    col_port.grid(row=0, column=2, sticky="ew", padx=(8, 0))
    champ_label(col_port, "Port")
    champ_port = tk.Entry(
        col_port, width=7, justify="center", font=FONT_INPUT,
        relief="solid", bd=1, highlightthickness=1,
        highlightbackground=COLOR_BORDER, highlightcolor=COLOR_SECONDARY,
    )
    champ_port.insert(0, "8000")
    champ_port.pack(ipady=6, fill="x")

    tk.Label(
        body,
        text="L'agent sera installé comme un service système\net démarrera automatiquement à chaque redémarrage.",
        bg=COLOR_CARD,
        fg=COLOR_MUTED,
        justify="center",
        font=FONT_SMALL,
    ).pack(pady=(18, 16))

    # ---------- Bloc conditions ----------
    frame_conditions = tk.Frame(
        body, bg=COLOR_INFO_BG,
        highlightbackground=COLOR_INFO_BORDER, highlightthickness=1,
    )
    frame_conditions.pack(fill="x", pady=(0, 4))

    texte_conditions = (
        " En poursuivant l'installation, vous acceptez que Smart SIEM Agent puisse :\n\n"
        " ✓ Collecter les journaux système\n"
        " ✓ Surveiller les processus actifs\n"
        " ✓ Analyser les connexions réseau\n"
        " ✓ Recevoir des actions SOAR du serveur\n"
        " ✓ Fonctionner en arrière-plan avec les privilèges administrateur"
    )
    label_conditions = tk.Label(
        frame_conditions, text=texte_conditions, bg=COLOR_INFO_BG, fg=COLOR_TEXT,
        justify="left", 
        anchor="w",       
        wraplength=380,    
        font=FONT_SMALL,
    )
    label_conditions.pack( padx=16, pady=14, fill="x" )

    # ---------- Statut (retour visuel avant messagebox) ----------
    label_statut = tk.Label(body, text="", bg=COLOR_CARD, font=FONT_SMALL,)
    label_statut.pack(pady=(10, 0))

    # ---------- Bouton d'action ----------
    def au_survol(_e):
        bouton_installer.configure(bg="#0d3d8f")

    def au_depart(_e):
        bouton_installer.configure(bg=COLOR_PRIMARY)

    def au_clic_bouton():
        protocole = combo_protocol.get()
        hote = champ_hote.get().strip()
        port = champ_port.get().strip()

        if not hote:
            messagebox.showwarning("Attention", "Veuillez renseigner l'adresse hôte du serveur.")
            return
        if not port:
            messagebox.showwarning("Attention", "Veuillez renseigner le port d'écoute.")
            return
        if not port.isdigit():
            messagebox.showwarning("Attention", "Le port doit être un nombre entier valide (ex: 8000).")
            return

        bouton_installer.configure(state="disabled", text="Installation en cours...")
        label_statut.configure(text="Configuration du service en cours, merci de patienter...", fg=COLOR_MUTED)
        fenetre.update_idletasks()

        try:
            installer_agent_systeme(protocole, hote, port)
            label_statut.configure(text="Installation réussie.", fg=COLOR_SUCCESS)
            messagebox.showinfo(
                "Succès",
                "L'agent Smart SIEM a été configuré et installé en arrière-plan avec succès !",
            )
            fenetre.destroy()
        except Exception as e:
            label_statut.configure(text="Échec de l'installation.", fg=COLOR_ERROR)
            bouton_installer.configure(state="normal", text="Installer & Démarrer l'agent")
            messagebox.showerror("Erreur d'installation", f"Impossible d'installer le service :\n{str(e)}")

    bouton_installer = tk.Button(
        body,
        text="Installer & Démarrer l'agent",
        command=au_clic_bouton,
        bg=COLOR_PRIMARY,
        fg="white",
        activebackground="#0d3d8f",
        activeforeground="white",
        font=FONT_BUTTON,
        relief="flat",
        bd=0,
        cursor="hand2",
    )
    bouton_installer.pack(fill="x", ipady=10, pady=(14, 0))
    bouton_installer.bind("<Enter>", au_survol)
    bouton_installer.bind("<Leave>", au_depart)

    # ---------- Footer ----------
    tk.Label(
        card, text="Smart SIEM © 2026", bg=COLOR_CARD, fg="#9AA5B1", font=FONT_SMALL,
    ).pack(side="bottom", pady=12)

    fenetre.mainloop()




    