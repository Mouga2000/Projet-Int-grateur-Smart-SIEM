from pathlib import Path

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.post("/api/v1/events")
async def receive(event: dict):

    print(event)

    return {"status": "ok"}


@app.post("/api/v1/agents/heartbeat")
async def heartbeat(data: dict):

    print("=" * 50)
    print("Heartbeat reçu")
    print(data)
    print("=" * 50)

    return {"status": "received"}


@app.get("/api/v1/ping")
async def ping():

    print("=" * 50)
    print("[PING] Un client vérifie la disponibilité du serveur SIEM.")
    print("=" * 50)

    return {"status": "ok"}





if __name__ == "__main__":
    cert_dir = Path(__file__).parent / "security"
    
    cert_file = cert_dir / "siem-server.crt"
    key_file = cert_dir / "siem-server.key"

    # --- Lignes de vérification de l'activation TLS ---
    print("=" * 50)
    if cert_file.exists() and key_file.exists():
        print("🔒 [SUCCÈS] Sécurité TLS activée : Chargement des certificats.")
        print(f"   -> Certificat : {cert_file.name}")
        print(f"   -> Clé privée : {key_file.name}")
        print("🚀 Le serveur SIEM va démarrer en mode sécurisé (HTTPS)")
    else:
        print("⚠️ [ERREUR] Impossible d'activer le protocole TLS.")
        print(f"   Veuillez vérifier que le dossier '{cert_dir.name}' contient vos fichiers .crt et .key")
    print("=" * 50)

    uvicorn.run(
        "main:app",            # remplace "main" par le nom de ton fichier si nécessaire
        host="0.0.0.0",
        port=8000,
        reload=False,

        ssl_certfile=str(cert_file),
        ssl_keyfile=str(key_file),
    )
