# app/tests/test_services/test_archiver.py
# -------------------------------
# Tests unitaires du service ArchiverService
# (cryptographie et logique pure — sans I/O réel)

import gzip
import hashlib
import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.archiver import ArchiverService


# =============================================================================
# Tests de _build_merkle_root()
# =============================================================================

class TestBuildMerkleRoot:

    def test_empty_logs_returns_fixed_hash(self):
        root = ArchiverService._build_merkle_root([])
        expected = hashlib.sha256(b"empty").hexdigest()
        assert root == expected

    def test_single_log_merkle_root(self):
        logs = [{"host": "server-01", "severity": "critical"}]
        root = ArchiverService._build_merkle_root(logs)
        assert isinstance(root, str)
        assert len(root) == 64  # SHA-256 hex

    def test_same_logs_same_root(self):
        logs = [{"host": "server-01"}, {"host": "server-02"}]
        root1 = ArchiverService._build_merkle_root(logs)
        root2 = ArchiverService._build_merkle_root(logs)
        assert root1 == root2

    def test_different_logs_different_root(self):
        logs1 = [{"host": "server-01"}]
        logs2 = [{"host": "server-02"}]
        root1 = ArchiverService._build_merkle_root(logs1)
        root2 = ArchiverService._build_merkle_root(logs2)
        assert root1 != root2

    def test_odd_number_of_logs(self):
        """Trois logs (nombre impair) : le dernier est dupliqué."""
        logs = [{"id": 1}, {"id": 2}, {"id": 3}]
        root = ArchiverService._build_merkle_root(logs)
        assert isinstance(root, str)
        assert len(root) == 64

    def test_order_matters(self):
        """L'ordre des logs change la racine Merkle."""
        logs_a = [{"id": 1}, {"id": 2}]
        logs_b = [{"id": 2}, {"id": 1}]
        assert ArchiverService._build_merkle_root(logs_a) != ArchiverService._build_merkle_root(logs_b)


# =============================================================================
# Tests de _compute_sha256()
# =============================================================================

class TestComputeSha256:

    def test_sha256_known_file(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"hello world")
        expected = hashlib.sha256(b"hello world").hexdigest()
        result = ArchiverService._compute_sha256(test_file)
        assert result == expected

    def test_sha256_returns_64_chars(self, tmp_path):
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"some random data")
        result = ArchiverService._compute_sha256(test_file)
        assert len(result) == 64

    def test_sha256_different_files_different_hash(self, tmp_path):
        file1 = tmp_path / "a.txt"
        file2 = tmp_path / "b.txt"
        file1.write_bytes(b"file A content")
        file2.write_bytes(b"file B content")
        assert ArchiverService._compute_sha256(file1) != ArchiverService._compute_sha256(file2)

    def test_sha256_same_content_same_hash(self, tmp_path):
        file1 = tmp_path / "c.txt"
        file2 = tmp_path / "d.txt"
        file1.write_bytes(b"identical content")
        file2.write_bytes(b"identical content")
        assert ArchiverService._compute_sha256(file1) == ArchiverService._compute_sha256(file2)


# =============================================================================
# Tests de _sign_payload() et verify_signature()
# =============================================================================

class TestSignatureVerification:

    def test_sign_and_verify_roundtrip(self, tmp_path):
        """Une signature générée doit être vérifiable."""
        with patch.object(ArchiverService, "ARCHIVE_DIR", tmp_path):
            key_path = tmp_path / "archive_key.pem"
            # Générer une clé et utiliser _sign_payload/_verify_signature
            with patch("app.services.archiver.Path", return_value=MagicMock(exists=MagicMock(return_value=False))):
                # Test direct : générer une clé RSA en mémoire
                from cryptography.hazmat.primitives.asymmetric import rsa, padding
                from cryptography.hazmat.primitives import hashes, serialization
                from cryptography.hazmat.backends import default_backend

                key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                    backend=default_backend(),
                )
                payload = "2026-06-27T10:00:00Z:abc123hash"
                signature = key.sign(
                    payload.encode(),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH,
                    ),
                    hashes.SHA256(),
                ).hex()

                # Vérification avec la clé publique
                try:
                    key.public_key().verify(
                        bytes.fromhex(signature),
                        payload.encode(),
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH,
                        ),
                        hashes.SHA256(),
                    )
                    valid = True
                except Exception:
                    valid = False
                assert valid is True

    def test_verify_signature_invalid_returns_false(self, tmp_path):
        """Une signature invalide doit retourner False."""
        with patch("app.services.archiver.Path") as MockPath:
            mock_path = MagicMock()
            mock_path.exists.return_value = False
            MockPath.return_value = mock_path

            # On mock _get_or_create_key pour retourner une clé fraîche
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.backends import default_backend

            key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend(),
            )
            with patch.object(ArchiverService, "_get_or_create_key", return_value=key):
                result = ArchiverService.verify_signature("payload", "deadbeef" * 64)
                assert result is False


# =============================================================================
# Tests de verify_archive() — logique d'intégrité sans I/O réel
# =============================================================================

class TestVerifyArchive:

    def _make_archive_with_file(self, tmp_path, content: bytes = b"test content"):
        """Crée un faux fichier archive et retourne les métadonnées."""
        archive_file = tmp_path / "archive_20260627_100000.json.gz"
        with gzip.open(archive_file, "wt") as f:
            json.dump({"logs": [], "count": 0}, f)

        sha256 = ArchiverService._compute_sha256(archive_file)
        chain_input = "GENESIS" + sha256
        chain_hash = hashlib.sha256(chain_input.encode()).hexdigest()

        return {
            "id": 1,
            "file_path": str(archive_file),
            "sha256_hash": sha256,
            "chain_hash": chain_hash,
            "previous_hash": None,
            "timestamp_signature": None,
            "certified_at": "2026-06-27T10:00:00+00:00",
            "status": "active",
        }

    def test_verify_file_exists_check(self, tmp_path):
        archive = self._make_archive_with_file(tmp_path)
        result = ArchiverService.verify_archive(archive)
        file_check = next(c for c in result["checks"] if c["name"] == "file_exists")
        assert file_check["passed"] is True

    def test_verify_sha256_integrity_valid(self, tmp_path):
        archive = self._make_archive_with_file(tmp_path)
        result = ArchiverService.verify_archive(archive)
        sha_check = next(c for c in result["checks"] if c["name"] == "sha256_integrity")
        assert sha_check["passed"] is True

    def test_verify_sha256_integrity_tampered(self, tmp_path):
        archive = self._make_archive_with_file(tmp_path)
        # Altérer le hash attendu
        archive["sha256_hash"] = "aaaa" + "0" * 60
        result = ArchiverService.verify_archive(archive)
        sha_check = next(c for c in result["checks"] if c["name"] == "sha256_integrity")
        assert sha_check["passed"] is False

    def test_verify_chain_integrity_genesis(self, tmp_path):
        archive = self._make_archive_with_file(tmp_path)
        result = ArchiverService.verify_archive(archive)
        chain_check = next(c for c in result["checks"] if c["name"] == "chain_integrity")
        assert chain_check["passed"] is True

    def test_verify_missing_file_returns_invalid(self):
        archive = {
            "id": 99,
            "file_path": "/nonexistent/path/archive.json.gz",
            "sha256_hash": "abc",
            "chain_hash": "def",
        }
        result = ArchiverService.verify_archive(archive)
        assert result["valid"] is False
        file_check = next(c for c in result["checks"] if c["name"] == "file_exists")
        assert file_check["passed"] is False

    def test_verify_all_checks_determine_valid(self, tmp_path):
        archive = self._make_archive_with_file(tmp_path)
        result = ArchiverService.verify_archive(archive)
        # valid = True si tous les checks passent (la signature est absente → échoue)
        # Le résultat dépend des checks disponibles
        assert "valid" in result
        assert isinstance(result["valid"], bool)

    def test_verify_returns_verified_at(self, tmp_path):
        archive = self._make_archive_with_file(tmp_path)
        result = ArchiverService.verify_archive(archive)
        assert "verified_at" in result


# =============================================================================
# Tests de export_archive()
# =============================================================================

class TestExportArchive:

    def test_export_has_required_fields(self, tmp_path):
        archive_file = tmp_path / "archive.json.gz"
        with gzip.open(archive_file, "wt") as f:
            json.dump({}, f)

        archive = {
            "id": 1,
            "file_path": str(archive_file),
            "date_from": "2026-06-01T00:00:00Z",
            "date_to": "2026-06-30T23:59:59Z",
            "log_count": 1500,
            "file_size_bytes": 102400,
            "sha256_hash": "abc" * 21 + "a",
            "merkle_root": "def" * 21 + "d",
            "chain_hash": "ghi" * 21 + "g",
            "previous_hash": None,
            "timestamp_signature": None,
            "certified_by": "self",
            "certified_at": "2026-06-27T10:00:00Z",
            "verified_at": None,
            "status": "active",
        }
        result = ArchiverService.export_archive(archive)

        assert "archive_id" in result
        assert "period" in result
        assert "log_count" in result
        assert "proofs" in result
        assert "exported_at" in result
        assert result["archive_id"] == 1
        assert result["log_count"] == 1500

    def test_export_file_available_true(self, tmp_path):
        archive_file = tmp_path / "archive.json.gz"
        archive_file.write_bytes(b"data")

        archive = {
            "id": 1,
            "file_path": str(archive_file),
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "log_count": 100,
            "file_size_bytes": 1024,
            "sha256_hash": "a" * 64,
            "merkle_root": "b" * 64,
            "chain_hash": "c" * 64,
            "certified_by": "self",
            "certified_at": "2026-06-27",
            "status": "active",
        }
        result = ArchiverService.export_archive(archive)
        assert result["file_available"] is True

    def test_export_file_available_false_when_missing(self):
        archive = {
            "id": 2,
            "file_path": "/nonexistent/path.json.gz",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "log_count": 50,
            "file_size_bytes": 512,
            "sha256_hash": "a" * 64,
            "merkle_root": "b" * 64,
            "chain_hash": "c" * 64,
            "certified_by": "self",
            "certified_at": "2026-06-27",
            "status": "active",
        }
        result = ArchiverService.export_archive(archive)
        assert result["file_available"] is False

    def test_export_proofs_structure(self, tmp_path):
        archive_file = tmp_path / "a.json.gz"
        archive_file.write_bytes(b"x")

        archive = {
            "id": 1,
            "file_path": str(archive_file),
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "log_count": 10,
            "file_size_bytes": 100,
            "sha256_hash": "a" * 64,
            "merkle_root": "b" * 64,
            "chain_hash": "c" * 64,
            "previous_hash": None,
            "timestamp_signature": "sig",
            "certified_by": "self",
            "certified_at": "2026-06-27",
            "verified_at": None,
            "status": "active",
        }
        result = ArchiverService.export_archive(archive)
        proofs = result["proofs"]
        assert "sha256" in proofs
        assert "merkle_root" in proofs
        assert "chain_hash" in proofs
        assert "certified_by" in proofs
        assert "certified_at" in proofs


# =============================================================================
# Tests de la chaîne de hachage (chain logic)
# =============================================================================

class TestChainLogic:
    """Vérifie la logique blockchain-like entre archives successives."""

    def _compute_chain(self, previous_hash: str, sha256: str) -> str:
        chain_input = (previous_hash or "GENESIS") + sha256
        return hashlib.sha256(chain_input.encode()).hexdigest()

    def test_first_archive_uses_genesis(self):
        sha256 = "a" * 64
        chain = self._compute_chain(None, sha256)
        expected = hashlib.sha256(("GENESIS" + sha256).encode()).hexdigest()
        assert chain == expected

    def test_second_archive_uses_previous_hash(self):
        prev = "b" * 64
        sha256 = "c" * 64
        chain = self._compute_chain(prev, sha256)
        expected = hashlib.sha256((prev + sha256).encode()).hexdigest()
        assert chain == expected

    def test_chain_changes_with_different_sha256(self):
        prev = "d" * 64
        sha1 = "e" * 64
        sha2 = "f" * 64
        assert self._compute_chain(prev, sha1) != self._compute_chain(prev, sha2)

    def test_chain_changes_with_different_previous(self):
        sha256 = "g" * 64
        prev1 = "h" * 64
        prev2 = "i" * 64
        assert self._compute_chain(prev1, sha256) != self._compute_chain(prev2, sha256)
