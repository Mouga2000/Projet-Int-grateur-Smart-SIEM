import os
import tkinter as tk
from tkinter import messagebox
from code.installation import installer_agent_systeme


def lancer_assistant_graphique() -> None:

    fenetre = tk.Tk()
    fenetre.title("Smart SIEM Agent")
    fenetre.geometry("560x680")
    fenetre.resizable(True, True)
    fenetre.configure(bg="#F4F7FA")

    # ===========================
    # Couleurs
    # ===========================

    COLOR_PRIMARY = "#0A2F6F"
    COLOR_SECONDARY = "#1E88E5"
    COLOR_BG = "#F4F7FA"
    COLOR_CARD = "#FFFFFF"
    COLOR_TEXT = "#1E293B"
    COLOR_RED = "#C62828"

    # ===========================
    # Carte centrale
    # ===========================

    card = tk.Frame(
        fenetre,
        bg=COLOR_CARD,
        bd=0,
        highlightthickness=1,
        highlightbackground="#D9E2EC"
    )

    card.place(relx=0.5, rely=0.5, anchor="center", width=500, height=600)

    # ===========================
    # Logo
    # ===========================

    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")

    if os.path.exists(logo_path):
        try:
            logo = tk.PhotoImage(file=logo_path)

            logo_label = tk.Label(
                card,
                image=logo,
                bg="white"
            )

            logo_label.image = logo
            logo_label.pack(pady=(20,8))

        except:
            pass

    # ===========================
    # Titre
    # ===========================

    tk.Label(
        card,
        text="AGENT SMART SIEM",
        bg="white",
        fg=COLOR_PRIMARY,
        font=("Segoe UI",18,"bold")
    ).pack()

    tk.Label(
        card,
        text="Assistant d'installation",
        bg="white",
        fg=COLOR_SECONDARY,
        font=("Segoe UI",11)
    ).pack(pady=(0,20))

    # ===========================

    tk.Label(
        card,
        text="Adresse IP du serveur SIEM",
        bg="white",
        fg=COLOR_TEXT,
        font=("Segoe UI",11,"bold")
    ).pack()

    champ_ip = tk.Entry(
        card,
        width=30,
        justify="center",
        font=("Segoe UI",12),
        relief="solid",
        bd=1
    )

    champ_ip.insert(0, "192.168.204.132")
    champ_ip.pack(ipady=6,pady=12)

    # ===========================
    # Description
    # ===========================

    tk.Label(
        card,
        text="L'agent sera installé comme un service système\n"
             "et démarrera automatiquement à chaque démarrage.",
        bg="white",
        fg="#5C6773",
        justify="center",
        font=("Segoe UI",10)
    ).pack(pady=(0,20))

    # ===========================
    # Conditions
    # ===========================

    frame_conditions = tk.Frame(
        card,
        bg="#EDF5FF",
        highlightbackground="#C5D9F1",
        highlightthickness=1
    )

    frame_conditions.pack(
        padx=20,
        fill="x",
        pady=10
    )

    texte = (
        "En poursuivant l'installation vous acceptez que "
        "Smart SIEM Agent puisse :\n\n"

        "✓ Collecter les journaux système\n"
        "✓ Surveiller les processus actifs\n"
        "✓ Analyser les connexions réseau\n"
        "✓ Recevoir des actions SOAR du serveur\n"
        "✓ Fonctionner en arrière-plan avec les privilèges administrateur"
    )

    tk.Label(
        frame_conditions,
        text=texte,
        bg="#EDF5FF",
        fg=COLOR_TEXT,
        justify="left",
        wraplength=420,
        font=("Segoe UI",9)
    ).pack(
        padx=15,
        pady=15
    )

    # ===========================
    # Bouton
    # ===========================

    def au_clic_bouton():

        ip = champ_ip.get().strip()

        if not ip:
            messagebox.showwarning(
                "Attention",
                "Veuillez renseigner une adresse IP."
            )
            return

        installer_agent_systeme(ip)
        fenetre.destroy()

    bouton = tk.Button(
        card,
        text="Installer l'Agent",
        command=au_clic_bouton,
        bg=COLOR_PRIMARY,
        fg="white",
        activebackground=COLOR_SECONDARY,
        activeforeground="white",
        relief="flat",
        cursor="hand2",
        font=("Segoe UI",11,"bold"),
        padx=25,
        pady=10
    )

    bouton.pack(pady=25)

    # ===========================
    # Footer
    # ===========================

    tk.Label(
        card,
        text="Smart SIEM © 2026",
        bg="white",
        fg="#7C8793",
        font=("Segoe UI",9)
    ).pack(side="bottom", pady=15)

    fenetre.mainloop()



    