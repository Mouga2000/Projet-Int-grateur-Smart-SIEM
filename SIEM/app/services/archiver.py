# app/services/archiver.py
# -------------------------------
# Service d'archivage conforme : intégrité, chaîne de hachage, horodatage certifié

import gzip
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from app.core.config import settings
from app.repositories.archive_repo import ArchiveRepository
from app.repositories.log_repo import LogRepository


class ArchiverService:
    """
    Service d'archivage conforme aux exigences réglementaires :

    - SHA-256 sur chaque fichier d'archive
    - Merkle tree sur les logs individuels
    - Chaîne de hachage (blockchain-like) entre archives successives
    - Signature RSA de l'horodatage (non-répudiation)
    - Vérification d'intégrité à la demande
    """

    ARCHIVE_DIR = Path(settings.ARCHIVE_DIR)

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    @classmethod
    def _ensure_dirs(cls):
        """Crée le répertoire d'archives s'il n'existe pas."""
        cls.ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Hachage & Merkle
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_sha256(file_path: Path) -> str:
        """Calcule l'empreinte SHA-256 d'un fichier (streaming -> gros fichiers)."""
        sha = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha.update(chunk)
        return sha.hexdigest()

    @staticmethod
    def _build_merkle_root(logs: list[dict]) -> str:
        """
        Construit une racine Merkle à partir des hashs individuels des logs.
        Permet de vérifier qu'aucun log n'a été ajouté/supprimé/modifié.
        """
        if not logs:
            return hashlib.sha256(b"empty").hexdigest()

        # Niveau 0 : feuilles (hash de chaque log normalisé)
        leaves = [
            hashlib.sha256(
                json.dumps(log, sort_keys=True, default=str).encode()
            ).hexdigest()
            for log in logs
        ]

        # Niveaux supérieurs : combinaison par paire
        while len(leaves) > 1:
            if len(leaves) % 2 != 0:
                leaves.append(leaves[-1])  # Dupliquer le dernier si impair
            parents = []
            for i in range(0, len(leaves), 2):
                combined = hashlib.sha256(
                    (leaves[i] + leaves[i + 1]).encode()
                ).hexdigest()
                parents.append(combined)
            leaves = parents

        return leaves[0]

    # ------------------------------------------------------------------
    # Signature / Certification
    # ------------------------------------------------------------------

    @classmethod
    def _get_or_create_key(cls) -> rsa.RSAPrivateKey:
        """Charge ou génère la clé RSA pour signer les archives."""
        key_path = Path("certs/archive_key.pem")
        if key_path.exists():
            with open(key_path, "rb") as f:
                return serialization.load_pem_private_key(
                    f.read(), password=None, backend=default_backend()
                )

        # Générer une nouvelle clé
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )
        with open(key_path, "wb") as f:
            f.write(
                key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
        return key

    @classmethod
    def _sign_payload(cls, payload: str) -> str:
        """Signe un payload avec la clé privée RSA."""
        key = cls._get_or_create_key()
        signature = key.sign(
            payload.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return signature.hex()

    @classmethod
    def verify_signature(cls, payload: str, signature_hex: str) -> bool:
        """Vérifie une signature RSA."""
        try:
            key = cls._get_or_create_key()
            public_key = key.public_key()
            public_key.verify(
                bytes.fromhex(signature_hex),
                payload.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Création d'archive
    # ------------------------------------------------------------------

    @classmethod
    async def create_archive(
        cls,
        log_repo: LogRepository,
        archive_repo: ArchiveRepository,
        date_from: datetime,
        date_to: datetime,
        user_id: int,
    ) -> dict:
        """
        Crée une archive certifiée des logs sur une période donnée.

        Étapes :
        1. Récupère les logs depuis Elasticsearch
        2. Sauvegarde en fichier JSON compressé (gzip)
        3. Calcule SHA-256 du fichier + racine Merkle des logs
        4. Chaîne avec l'archive précédente (blockchain-like)
        5. Signe l'horodatage avec la clé RSA
        6. Persiste les métadonnées en PostgreSQL
        """
        cls._ensure_dirs()

        # 1. Récupérer les logs de la période
        result = await log_repo.search_by_date_range(date_from, date_to)
        if not result["items"]:
            raise ValueError("Aucun log trouvé dans cette période")

        logs = result["items"]
        log_count = result["total"]

        # 2. Générer le nom du fichier
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = cls.ARCHIVE_DIR / f"archive_{timestamp_str}.json.gz"

        # 3. Sauvegarder les logs compressés avec métadonnées
        archive_data = {
            "logs": logs,
            "count": log_count,
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "archived_at": datetime.now(timezone.utc).isoformat(),
        }
        with gzip.open(archive_file, "wt", encoding="utf-8") as f:
            json.dump(archive_data, f, indent=2, default=str)

        file_size = archive_file.stat().st_size

        # 4. Calculer les hashs
        sha256_hash = cls._compute_sha256(archive_file)
        merkle_root = cls._build_merkle_root(logs)

        # 5. Chaîne avec l'archive précédente
        last_archive = await archive_repo.get_last_archive()
        previous_hash = last_archive["chain_hash"] if last_archive else None
        previous_id = last_archive["id"] if last_archive else None

        chain_input = (previous_hash or "GENESIS") + sha256_hash
        chain_hash = hashlib.sha256(chain_input.encode()).hexdigest()

        # 6. Signer l'horodatage
        certified_at = datetime.now(timezone.utc)
        timestamp_payload = f"{certified_at.isoformat()}:{chain_hash}"
        signature = cls._sign_payload(timestamp_payload)

        # 7. Enregistrer en base
        archive = await archive_repo.create(
            {
                "date_from": date_from,
                "date_to": date_to,
                "log_count": log_count,
                "file_path": str(archive_file),
                "file_size_bytes": file_size,
                "sha256_hash": sha256_hash,
                "merkle_root": merkle_root,
                "previous_archive_id": previous_id,
                "previous_hash": previous_hash,
                "chain_hash": chain_hash,
                "timestamp_signature": signature,
                "certified_by": "self",
                "certified_at": certified_at,
                "created_by": user_id,
                "status": "active",
            }
        )

        return archive

    # ------------------------------------------------------------------
    # Vérification d'intégrité
    # ------------------------------------------------------------------

    @classmethod
    def verify_archive(cls, archive: dict) -> dict:
        """
        Vérifie l'intégrité complète d'une archive :
        - Existence du fichier
        - SHA-256 correspondant
        - Chaîne de hachage valide
        - Signature temporelle valide
        """
        result = {
            "archive_id": archive["id"],
            "checks": [],
            "valid": False,
        }

        # Vérification 1 : existence du fichier
        file_path = Path(archive["file_path"])
        if not file_path.exists():
            result["checks"].append(
                {
                    "name": "file_exists",
                    "passed": False,
                    "detail": "Fichier d'archive introuvable",
                }
            )
            result["valid"] = False
            return result
        result["checks"].append(
            {
                "name": "file_exists",
                "passed": True,
            }
        )

        # Vérification 2 : intégrité SHA-256
        actual_hash = cls._compute_sha256(file_path)
        hash_ok = actual_hash == archive["sha256_hash"]
        result["checks"].append(
            {
                "name": "sha256_integrity",
                "passed": hash_ok,
                "expected": archive["sha256_hash"],
                "actual": actual_hash,
            }
        )

        # Vérification 3 : chaîne de confiance (chain_hash)
        if archive.get("previous_hash"):
            expected_chain = hashlib.sha256(
                (archive["previous_hash"] + archive["sha256_hash"]).encode()
            ).hexdigest()
        else:
            expected_chain = hashlib.sha256(
                ("GENESIS" + archive["sha256_hash"]).encode()
            ).hexdigest()

        chain_ok = expected_chain == archive["chain_hash"]
        result["checks"].append(
            {
                "name": "chain_integrity",
                "passed": chain_ok,
            }
        )

        # Vérification 4 : signature temporelle
        if archive.get("timestamp_signature"):
            payload = f"{archive['certified_at']}:{archive['chain_hash']}"
            sig_ok = cls.verify_signature(payload, archive["timestamp_signature"])
            result["checks"].append(
                {
                    "name": "timestamp_signature",
                    "passed": sig_ok,
                }
            )
        else:
            result["checks"].append(
                {
                    "name": "timestamp_signature",
                    "passed": False,
                    "detail": "Aucune signature",
                }
            )

        result["valid"] = all(c["passed"] for c in result["checks"])
        result["verified_at"] = datetime.now(timezone.utc).isoformat()
        return result

    # ------------------------------------------------------------------
    # Export pour audit réglementaire
    # ------------------------------------------------------------------

    @classmethod
    def export_archive(cls, archive: dict) -> dict:
        """
        Génère un rapport d'export pour audit réglementaire.
        Contient toutes les preuvres (hashs, signature, chaîne).
        """
        file_path = Path(archive["file_path"])
        file_exists = file_path.exists()

        return {
            "archive_id": archive["id"],
            "period": f"{archive['date_from']} → {archive['date_to']}",
            "log_count": archive["log_count"],
            "file_size_bytes": archive["file_size_bytes"],
            "file_available": file_exists,
            "proofs": {
                "sha256": archive["sha256_hash"],
                "merkle_root": archive["merkle_root"],
                "chain_hash": archive["chain_hash"],
                "previous_hash": archive.get("previous_hash", "GENESIS"),
                "timestamp_signature": archive.get("timestamp_signature"),
                "certified_by": archive["certified_by"],
                "certified_at": archive["certified_at"],
                "last_verified_at": archive.get("verified_at"),
                "status": archive["status"],
            },
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }
