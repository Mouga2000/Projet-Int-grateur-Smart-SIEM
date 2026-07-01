from flask import Flask, request, jsonify
import threading
import time

app = Flask(__name__)

# Base de données en mémoire pour suivre l'état des agents
agents_db = {
    "ubuntu-server-erp-01": {"last_seen": time.time(), "status": "unknown"}
}

# File d'attente des commandes descendantes à envoyer aux agents
# (En production, utilisez une base de données ou Redis)
pending_commands = {
    "ubuntu-server-erp-01": "KILL_PROCESS_99" # Exemple de commande en attente
}

TIMEOUT_LIMIT = 30  # 30 secondes sans heartbeat = extinction brutale ou crash

# 1. API Endpoint : Réception du Heartbeat
@app.route('/api/heartbeat', methods=['POST'])
def receive_heartbeat():
    # (Ajouter ici la vérification du token JWT dans les headers en prod)
    data = request.json
    agent_id = data.get("agent_id")
    status = data.get("status")
    
    if not agent_id:
        return jsonify({"error": "Missing agent_id"}), 400

    print(f"[Heartbeat] Reçu de {agent_id} | Statut déclaré : {status}")

    if status == "stopping":
        # Scénario 1 : L'agent s'éteint proprement
        agents_db[agent_id] = {"last_seen": time.time(), "status": "offline_clean"}
        print(f"[INFO] L'agent {agent_id} s'est éteint proprement. Aucune alerte.")
        return jsonify({"message": "Goodbye acknowledged"}), 200
        
    else:
        # Statut "alive" : On met à jour l'heure de dernière activité
        agents_db[agent_id] = {"last_seen": time.time(), "status": "online"}
        
        # On vérifie si une commande descendante attend cet agent
        response_data = {"message": "Heartbeat OK"}
        if agent_id in pending_commands and pending_commands[agent_id]:
            response_data["command"] = pending_commands[agent_id]
            # On supprime la commande une fois transmise dans la réponse
            pending_commands[agent_id] = None 
            
        return jsonify(response_data), 200

# 2. Thread de Surveillance : Détection des extinctions brutales
def monitor_agents_timeout():
    while True:
        current_time = time.time()
        for agent_id, info in list(agents_db.items()):
            # Si l'agent était en ligne mais ne répond plus
            if info["status"] == "online" and (current_time - info["last_seen"]) > TIMEOUT_LIMIT:
                # Scénario 2 : Extinction brutale constatée
                info["status"] = "crash_detected"
                trigger_critical_alert(agent_id)
                
        time.sleep(5) # Vérification toutes les 5 secondes

def trigger_critical_alert(agent_id):
    print(f"\n[!!!] ALERTE SÉCURITÉ CRITIQUE : L'agent {agent_id} ne répond plus !")
    print(f"[!!!] Cause suspectée : Extinction brutale, coupure réseau ou sabotage.\n")

if __name__ == '__main__':
    # Lancement du thread de surveillance en arrière-plan
    threading.Thread(target=monitor_agents_timeout, daemon=True).start()
    
    # Lancement du serveur SIEM (Simulation HTTPS en local)
    app.run(port=5000)


