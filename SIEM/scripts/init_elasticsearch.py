#!/usr/bin/env python
"""
Script d'initialisation d'Elasticsearch pour le projet Smart SIEM
À exécuter une fois lors du déploiement initial.
Usage: python -m scripts.init_elasticsearch
"""

import asyncio
from elasticsearch import AsyncElasticsearch
from app.core.config import settings

# Mapping de l'index "users"
USER_INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "username": {"type": "keyword"},
            "email": {"type": "keyword"},
            "password_hash": {"type": "keyword"},
            "mfa_secret": {"type": "keyword"},
            "mfa_enabled": {"type": "boolean"},
            "role": {"type": "keyword"},
            "perimeter": {"type": "keyword"},
            "created_at": {"type": "date"},
            "last_login": {"type": "date"},
            "is_active": {"type": "boolean"}
        }
    }
}

# Mapping de l'index "audit"
AUDIT_INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "user_id": {"type": "keyword"},
            "username": {"type": "keyword"},
            "action": {"type": "keyword"},
            "result": {"type": "keyword"},
            "timestamp": {"type": "date"},
            "ip_address": {"type": "ip"},
            "details": {"type": "object", "enabled": True}
        }
    }
}

async def create_index(es: AsyncElasticsearch, index_name: str, mapping: dict):
    """Crée un index Elasticsearch s'il n'existe pas déjà"""
    if await es.indices.exists(index=index_name):
        print(f"L'index '{index_name}' existe déjà.")
        return
    
    await es.indices.create(index=index_name, body=mapping)
    print(f" Index '{index_name}' créé avec succès.")

async def main():
    """Point d'entrée du script"""
    print("Initialisation des index Elasticsearch...")
    
    es = AsyncElasticsearch(
        hosts=[f"{settings.ELASTICSEARCH_SCHEME}://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"]
    )
    
    try:
        # Vérifier la connexion
        await es.info()
        print(f"Connexion à Elasticsearch établie.")
        
        # Créer les index
        await create_index(es, settings.ELASTICSEARCH_INDEX_USERS, USER_INDEX_MAPPING)
        await create_index(es, settings.ELASTICSEARCH_INDEX_AUDIT, AUDIT_INDEX_MAPPING)
        
        print("\nInitialisation terminée avec succès.")
        
    except Exception as e:
        print(f"Erreur lors de l'initialisation: {e}")
        raise
    finally:
        await es.close()

if __name__ == "__main__":
    asyncio.run(main())