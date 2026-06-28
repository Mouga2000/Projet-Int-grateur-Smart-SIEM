# app/tests/test_core_security.py
# -------------------------------
# Tests unitaires des fonctions de sécurité (hash, JWT, MFA)

import time
import pytest
from datetime import timedelta
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_mfa_secret,
    get_mfa_uri,
    verify_mfa,
)


class TestPasswordHashing:

    def test_hash_password_returns_string(self):
        hashed = hash_password("monMotDePasse123!")
        assert isinstance(hashed, str)
        assert len(hashed) > 20

    def test_verify_password_correct(self):
        hashed = hash_password("monMotDePasse123!")
        assert verify_password("monMotDePasse123!", hashed) is True

    def test_verify_password_incorrect(self):
        hashed = hash_password("monMotDePasse123!")
        assert verify_password("mauvaisMotDePasse", hashed) is False

    def test_same_password_different_hashes(self):
        """Même mot de passe doit produire des hash différents (sel)."""
        h1 = hash_password("password123")
        h2 = hash_password("password123")
        assert h1 != h2

    def test_verify_empty_password(self):
        hashed = hash_password("validpassword")
        assert verify_password("", hashed) is False

    def test_verify_wrong_hash(self):
        with pytest.raises((ValueError, Exception)):
            verify_password("password", "hash_invalide")


class TestJWTTokens:

    def test_create_access_token_returns_string(self):
        token = create_access_token({"sub": "admin"})
        assert isinstance(token, str)
        assert token.count(".") == 2  # JWT a 3 parties

    def test_decode_valid_token(self):
        data = {"sub": "admin", "role": "administrateur"}
        token = create_access_token(data)
        decoded = decode_token(token)
        assert decoded["sub"] == "admin"
        assert decoded["role"] == "administrateur"
        assert decoded["type"] == "access"

    def test_decode_refresh_token(self):
        token = create_refresh_token({"sub": "user1"})
        decoded = decode_token(token)
        assert decoded["type"] == "refresh"
        assert decoded["sub"] == "user1"

    def test_decode_invalid_token_raises_error(self):
        with pytest.raises(ValueError, match="Token invalide"):
            decode_token("token.invalide.123")

    def test_token_contains_expected_claims(self):
        token = create_access_token({"sub": "admin", "role": "analyste", "perimeter": ["equipe"]})
        decoded = decode_token(token)
        assert decoded["sub"] == "admin"
        assert decoded["role"] == "analyste"
        assert decoded["perimeter"] == ["equipe"]

    def test_access_token_contains_exp(self):
        token = create_access_token({"sub": "admin"})
        decoded = decode_token(token)
        assert "exp" in decoded
        assert isinstance(decoded["exp"], (int, float))
        # L'expiration doit être dans le futur
        assert decoded["exp"] > time.time()


class TestMFA:

    def test_generate_mfa_secret_returns_string(self):
        secret = generate_mfa_secret()
        assert isinstance(secret, str)
        assert len(secret) > 10

    def test_generate_mfa_secret_unique(self):
        s1 = generate_mfa_secret()
        s2 = generate_mfa_secret()
        assert s1 != s2

    def test_get_mfa_uri_contains_expected_values(self):
        secret = generate_mfa_secret()
        uri = get_mfa_uri("admin", secret)
        assert "otpauth://totp/" in uri
        assert "admin" in uri
        assert "SmartSIEM" in uri

    def test_get_mfa_uri_custom_issuer(self):
        secret = generate_mfa_secret()
        uri = get_mfa_uri("user", secret, issuer="MonSIEM")
        assert "MonSIEM" in uri

    def test_verify_mfa_valid_code(self):
        """Test de vérification MFA avec un code généré."""
        secret = generate_mfa_secret()
        import pyotp
        totp = pyotp.TOTP(secret)
        code = totp.now()
        assert verify_mfa(secret, code) is True

    def test_verify_mfa_invalid_code(self):
        secret = generate_mfa_secret()
        assert verify_mfa(secret, "000000") is False

    def test_verify_mfa_empty_secret(self):
        assert verify_mfa("", "123456") is False

    def test_verify_mfa_empty_code(self):
        secret = generate_mfa_secret()
        assert verify_mfa(secret, "") is False

    def test_verify_mfa_none_values(self):
        assert verify_mfa(None, "123456") is False
        assert verify_mfa("secret", None) is False
