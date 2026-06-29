
```markdown
# Guide d'implémentation du profilage UEBA avec CLUE-LDS

**Version:** 1.0
**Date:** 28/06/2026
**Projet:** Smart SIEM - Moteur d'Analyse Comportementale (UEBA)

---

## 🎯 Objectif de ce guide

Ce document détaille les étapes pour utiliser le dataset **CLUE-LDS** (Cloud-based User Entity Behavior Analytics Log Data Set) afin de construire, entraîner et valider le module **UEBA** de votre Smart SIEM.

L'objectif est de transformer les 50 millions d'événements bruts du dataset en :
1.  Une **baseline comportementale** (profils) pour chaque utilisateur (horaires, volumes, géolocalisation).
2.  Un **score de risque dynamique** (0-100).
3.  Une **corrélation** entre ces scores et vos alertes de sécurité (pour générer des CRITICAL).

---

## 📁 1. Prérequis et Structure du Dataset

### 1.1. Fichier source
- **Fichier :** `clue.zip` (635 Mo) → décompressé en un fichier JSON (ou plusieurs) de ~14,5 Go.
- **Champs principaux :**
  ```json
  {
    "id": 21567530,
    "time": "2019-11-14T11:26:43Z",
    "uid": "intact-gray-marlin-trademarkagent", // Utilisateur
    "uidType": "name", // ou "ipaddress"
    "type": "login_successful", // Action
    "params": {"path": "/...", "user": "..."},
    "location": { // Géolocalisation (optionnelle)
      "countryCode": "AT",
      "city": "Gmunden",
      "timezone": "Europe/Vienna"
    },
    "isLocalIP": false,
    "role": "consulting" // Rôle métier
  }
```

### 1.2. Structure de votre projet

Assurez-vous que votre arborescence `app/` contient bien les fichiers suivants (créés lors du plan d'implémentation UEBA) :

- `app/services/ueba.py`
- `app/tasks/ueba_tasks.py`
- `app/models/sql_models.py` (avec la table `ueba_profiles`)

---

## ⚙️ 2. Étape 1 : Ingestion massive du dataset dans Elasticsearch

Avant de faire du Machine Learning, il faut que vos logs soient dans Elasticsearch (comme pour vos données CTU).

### 2.1. Script d'ingestion

Créez un script `scripts/ingest_clue_lds.py`. Il lit le fichier JSON ligne par ligne et les envoie à votre API `/ingest`.

```python
import json
import requests
from elasticsearch import helpers, Elasticsearch

# Configuration
ES_HOST = "http://localhost:9200"
INDEX_NAME = "logs-2026-06-28"  # Adaptez selon votre date

# 1. Lire le fichier CLUE décompressé
with open("clue.json", "r") as f:
    for line in f:
        event = json.loads(line)
      
        # 2. Mapper les champs CLUE vers votre schéma SIEM
        doc = {
            "@timestamp": event["time"],
            "user": event["uid"],
            "source_ip": event.get("ip", "0.0.0.0"),  # CLUE n'a pas toujours l'IP brute
            "log_type": event["type"],
            "severity": "INFO",  # Par défaut, ce n'est pas une alerte
            "raw_message": json.dumps(event),
            "decoded": {
                "uid_type": event.get("uidType"),
                "role": event.get("role"),
                "location": event.get("location"),
                "is_local_ip": event.get("isLocalIP", False),
                "params": event.get("params", {})
            },
            "perimeter": ["cloud"]  # Tag pour identifier cette source
        }
      
        # 3. Envoi vers Elasticsearch (via l'API pour déclencher votre normalisation, ou direct via helpers)
        # Option A : Direct Elasticsearch (plus rapide)
        helpers.bulk(ES, [{"_index": INDEX_NAME, "_source": doc}])
      
        # Option B : via votre API FastAPI (pour tester le pipeline complet)
        # requests.post("http://localhost:8000/api/v1/logs/ingest", json=doc)
```

### 2.2. Vérification

Lancez une requête dans Kibana pour vérifier que les logs sont bien indexés :

```json
GET /logs-*/_search
{
  "query": {"exists": {"field": "decoded.role"}}
}
```

---

## 🧪 3. Étape 2 : Feature Engineering (Extraction des indicateurs comportementaux)

Ici, nous ne faisons pas encore de ML. Nous construisons les **variables** (features) qui nourriront le modèle.

Créez une fonction dans `app/services/ueba.py` qui extrait ces features pour un utilisateur donné :

```python
def extract_features(events):
    """
    Args:
        events: Liste de dictionnaires (logs Elasticsearch)
    Returns:
        dict: Features calculées
    """
    hours = [datetime.fromisoformat(e["@timestamp"]).hour for e in events]
  
    # 1. Heures de connexion
    mean_hour = statistics.mean(hours) if hours else 0
    std_hour = statistics.stdev(hours) if len(hours) > 1 else 2.0
  
    # 2. Pays de connexion (distribution)
    countries = [e["decoded"]["location"]["countryCode"] for e in events if e.get("decoded", {}).get("location")]
  
    # 3. Taux de connexion externe vs interne
    total = len(events)
    external_count = sum(1 for e in events if e.get("decoded", {}).get("is_local_ip") is False)
    external_ratio = external_count / total if total > 0 else 0
  
    # 4. Volume d'accès aux fichiers
    file_ops = [e for e in events if e.get("log_type") == "file_accessed"]
    avg_file_ops = len(file_ops) / 7  # (moyenne par jour sur la semaine)
  
    return {
        "mean_hour": mean_hour,
        "std_hour": std_hour,
        "countries": countries,
        "external_ratio": external_ratio,
        "avg_daily_file_ops": avg_file_ops
    }
```

---

## 🤖 4. Étape 3 : Construction du Modèle (Approche hybride : Statistique + ML Léger)

Pour votre projet académique, je vous recommande une approche pragmatique, facile à expliquer en soutenance : **Un modèle "Isolation Forest" entraîné sur les features extraites**, combiné à un système de seuils pour les cas évidents.

### 4.1. Entraînement du modèle (Tâche Celery)

Créez `app/tasks/ueba_tasks.py` :

```python
from sklearn.ensemble import IsolationForest
import numpy as np
import pandas as pd
from app.services.ueba import extract_features

@app.task
def train_ueba_model():
    # 1. Récupérer les logs des 30 derniers jours depuis ES
    logs = es.search(index="logs-*", size=10000, body={...})  # 10k par batch
  
    # 2. Grouper par utilisateur
    users = {}
    for hit in logs:
        user = hit["_source"]["user"]
        if user not in users: users[user] = []
        users[user].append(hit["_source"])
  
    # 3. Extraire les features pour chaque utilisateur
    X = []
    user_ids = []
    for user, events in users.items():
        features = extract_features(events)
        # Sélectionner les features numériques pour le modèle
        row = [
            features["mean_hour"],
            features["std_hour"],
            features["external_ratio"],
            features["avg_daily_file_ops"]
        ]
        X.append(row)
        user_ids.append(user)
  
    # 4. Entraîner Isolation Forest
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X)  # X est une liste de listes (2D)
  
    # 5. Sauvegarder le modèle (ou le stocker en base)
    joblib.dump(model, "models/ueba_model.pkl")
  
    # 6. Stocker les baselines dans PostgreSQL
    for user, row in zip(user_ids, X):
        # Insérer ou mettre à jour la baseline dans la table ueba_profiles
        db.execute("""
            INSERT INTO ueba_profiles (user_id, baseline, last_updated)
            VALUES (%s, %s, NOW())
            ON CONFLICT (user_id) DO UPDATE SET baseline = %s
        """, (user, json.dumps({"features": row}), json.dumps({"features": row})))
  
    return {"status": "success", "users": len(user_ids)}
```

### 4.2. Inférence en temps réel (Scoring)

Lorsqu'un nouvel événement arrive, on calcule son score d'anomalie.

```python
# app/services/ueba.py
async def get_risk_score(self, user: str, event: dict) -> int:
    # 1. Charger le modèle (en cache)
    model = joblib.load("models/ueba_model.pkl")
  
    # 2. Extraire les features de l'événement courant
    current_features = extract_features([event])  # Une seule ligne
  
    # 3. Prédire l'anomalie (-1 = anomalie, 1 = normal)
    # Note : Isolation Forest retourne -1 pour les outliers
    prediction = model.predict([list(current_features.values())])[0]
  
    # 4. Calculer l'écart par rapport à la baseline (via z-score ou distance)
    baseline = await self.get_baseline(user)
    if baseline:
        # Calcul de la distance euclidienne entre le comportement actuel et la baseline
        distances = np.linalg.norm(np.array(list(current_features.values())) - np.array(baseline["features"]))
        risk_score = min(100, int(distances * 20))
    else:
        risk_score = 0
  
    # 5. Ajuster le score avec les règles métier (EX-F-032, EX-F-033)
    if event.get("decoded", {}).get("is_local_ip") is False and event.get("location", {}).get("countryCode") != baseline.get("usual_country"):
        risk_score += 30  # Connexion depuis l'étranger
  
    return min(100, risk_score)
```

---

## 🎭 5. Étape 4 : Simulation d'attaques (Validation)

Les auteurs du dataset CLUE-LDS fournissent une méthode pour simuler des **détournements de compte** en échangeant les comportements de deux utilisateurs.

### 5.1. Script de simulation

```python
# scripts/simulate_ueba_attack.py
def swap_users(user_a, user_b, dataset):
    """
    Échange les logs de l'utilisateur A avec ceux de l'utilisateur B
    pendant une période donnée (ex: 1 jour).
    """
    # Modifier le champ "uid" dans les logs pour les échanger
    # Envoyer ces logs modifiés dans votre SIEM
    pass
```

### 5.2. Validation

- **Avant l'attaque** : Le score UEBA des deux utilisateurs est bas (ex: 12).
- **Pendant l'attaque** : L'utilisateur A commence à agir comme B. Votre modèle (Isolation Forest) détecte un écart par rapport à sa baseline. Le score monte à 78.
- **Corrélation** : Associez ce score > 70 à une alerte réseau (ex: téléchargement massif). Votre moteur de corrélation génère une alerte **CRITICAL** (US-23).

---

## 🔄 6. Étape 5 : Automatisation du ré-entraînement (Celery Beat)

Les comportements des utilisateurs évoluent. Planifiez un ré-entraînement quotidien.

```python
# app/tasks/ueba_tasks.py (ajout)
from celery.schedules import crontab

app.conf.beat_schedule = {
    'retrain-ueba-every-night': {
        'task': 'app.tasks.ueba_tasks.train_ueba_model',
        'schedule': crontab(hour=2, minute=0),  # Tous les jours à 2h du matin
    },
}
```

---

## 📊 7. Synthèse des fichiers à modifier/créer

| Fichier                        | Action                                                                                             |
| :----------------------------- | :------------------------------------------------------------------------------------------------- |
| `scripts/ingest_clue_lds.py` | **Créer** : script d'import du dataset                                                      |
| `app/services/ueba.py`       | **Modifier** : ajouter `extract_features` et la logique d'inférence avec Isolation Forest |
| `app/tasks/ueba_tasks.py`    | **Créer** : tâche `train_ueba_model`                                                     |
| `app/core/config.py`         | Ajouter le chemin du modèle`UEBA_MODEL_PATH`                                                    |
| `requirements.txt`           | Ajouter`scikit-learn`, `joblib`, `pandas`, `numpy`                                         |

---

## 🚀 8. Lancer le pipeline complet

1. **Ingérer** les données :

   ```bash
   python scripts/ingest_clue_lds.py
   ```
2. **Entraîner** le premier modèle (en local ou via Celery) :

   ```bash
   python -c "from app.tasks.ueba_tasks import train_ueba_model; train_ueba_model()"
   ```
3. **Démarrer** les workers Celery (si ce n'est pas déjà fait) :

   ```bash
   celery -A app.tasks.celery worker --loglevel=info
   celery -A app.tasks.celery beat --loglevel=info
   ```
4. **Vérifier** dans votre dashboard que le `risk_score` s'affiche bien pour les utilisateurs du dataset CLUE-LDS.
