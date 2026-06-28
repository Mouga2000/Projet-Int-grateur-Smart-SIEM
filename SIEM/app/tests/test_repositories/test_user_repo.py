# app/tests/test_repositories/test_user_repo.py
# -------------------------------
# Tests unitaires du repository UserRepository
# (SQLAlchemy AsyncSession mockée — pas de base de données réelle)

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.repositories.user_repo import UserRepository


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_db():
    """Session SQLAlchemy asynchrone mockée."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.fixture
def user_repo(mock_db):
    return UserRepository(mock_db)


def _make_user_orm(
    id=1,
    username="admin",
    email="admin@siem.local",
    password_hash="$2b$12$hashed",
    role="administrateur",
    perimeter=None,
    is_active=True,
    mfa_enabled=False,
    mfa_secret=None,
    last_login=None,
    created_at=None,
    deleted_at=None,
):
    """Construit un objet ORM User factice."""
    user = MagicMock()
    user.id = id
    user.username = username
    user.email = email
    user.password_hash = password_hash
    user.role = role
    user.perimeter = perimeter or []
    user.is_active = is_active
    user.mfa_enabled = mfa_enabled
    user.mfa_secret = mfa_secret
    user.last_login = last_login
    user.created_at = created_at or datetime.now(timezone.utc)
    user.deleted_at = deleted_at
    return user


# =============================================================================
# Tests de create_user()
# =============================================================================

class TestCreateUser:

    @pytest.mark.asyncio
    async def test_create_user_returns_dict(self, user_repo, mock_db):
        user_orm = _make_user_orm(id=1, username="alice", email="alice@test.com")
        mock_db.refresh.side_effect = lambda u: None

        # simulate the db.refresh populating the user
        async def fake_refresh(obj):
            obj.id = 1
            obj.username = "alice"
            obj.email = "alice@test.com"
            obj.role = "analyste"
            obj.perimeter = []
            obj.is_active = True
            obj.mfa_enabled = False
            obj.mfa_secret = None
            obj.last_login = None
            obj.created_at = datetime.now(timezone.utc)

        mock_db.refresh = fake_refresh

        with patch("app.repositories.user_repo.hash_password", return_value="$2b$hashed"):
            with patch("app.repositories.user_repo.User") as MockUser:
                instance = _make_user_orm(id=1, username="alice", email="alice@test.com", role="analyste")
                MockUser.return_value = instance

                result = await user_repo.create_user({
                    "username": "alice",
                    "email": "alice@test.com",
                    "password": "password123",
                    "role": "analyste",
                    "perimeter": [],
                })

        assert isinstance(result, dict)
        assert result["username"] == "alice"
        assert result["email"] == "alice@test.com"

    @pytest.mark.asyncio
    async def test_create_user_hashes_password(self, user_repo, mock_db):
        """Le mot de passe doit être haché avant d'être stocké."""
        with patch("app.repositories.user_repo.hash_password", return_value="$2b$hashed") as mock_hash:
            with patch("app.repositories.user_repo.User") as MockUser:
                instance = _make_user_orm()
                MockUser.return_value = instance
                mock_db.refresh = AsyncMock()

                await user_repo.create_user({
                    "username": "bob",
                    "email": "bob@test.com",
                    "password": "secret123",
                    "role": "lecteur",
                })
                mock_hash.assert_called_once_with("secret123")


# =============================================================================
# Tests de get_user_by_username()
# =============================================================================

class TestGetUserByUsername:

    @pytest.mark.asyncio
    async def test_get_existing_user(self, user_repo, mock_db):
        user_orm = _make_user_orm(username="admin")
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = user_orm
        mock_db.execute.return_value = result_mock

        result = await user_repo.get_user_by_username("admin")
        assert result is not None
        assert result["username"] == "admin"

    @pytest.mark.asyncio
    async def test_get_nonexistent_user_returns_none(self, user_repo, mock_db):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = result_mock

        result = await user_repo.get_user_by_username("ghost")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_username_calls_db(self, user_repo, mock_db):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = result_mock

        await user_repo.get_user_by_username("testuser")
        mock_db.execute.assert_called_once()


# =============================================================================
# Tests de get_user_by_email()
# =============================================================================

class TestGetUserByEmail:

    @pytest.mark.asyncio
    async def test_get_existing_user_by_email(self, user_repo, mock_db):
        user_orm = _make_user_orm(email="admin@siem.local")
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = user_orm
        mock_db.execute.return_value = result_mock

        result = await user_repo.get_user_by_email("admin@siem.local")
        assert result is not None
        assert result["email"] == "admin@siem.local"

    @pytest.mark.asyncio
    async def test_get_nonexistent_email_returns_none(self, user_repo, mock_db):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = result_mock

        result = await user_repo.get_user_by_email("unknown@mail.com")
        assert result is None


# =============================================================================
# Tests de update_user()
# =============================================================================

class TestUpdateUser:

    @pytest.mark.asyncio
    async def test_update_existing_user_returns_true(self, user_repo, mock_db):
        user_orm = _make_user_orm(id=1, role="lecteur")
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = user_orm
        mock_db.execute.return_value = result_mock

        result = await user_repo.update_user(1, {"role": "analyste"})
        assert result is True

    @pytest.mark.asyncio
    async def test_update_nonexistent_user_returns_false(self, user_repo, mock_db):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = result_mock

        result = await user_repo.update_user(999, {"role": "analyste"})
        assert result is False

    @pytest.mark.asyncio
    async def test_update_user_sets_attribute(self, user_repo, mock_db):
        user_orm = _make_user_orm(id=1, role="lecteur")
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = user_orm
        mock_db.execute.return_value = result_mock

        await user_repo.update_user(1, {"role": "analyste"})
        assert user_orm.role == "analyste"


# =============================================================================
# Tests de update_last_login()
# =============================================================================

class TestUpdateLastLogin:

    @pytest.mark.asyncio
    async def test_update_last_login_existing_user(self, user_repo, mock_db):
        user_orm = _make_user_orm(username="admin", last_login=None)
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = user_orm
        mock_db.execute.return_value = result_mock

        result = await user_repo.update_last_login("admin")
        assert result is True
        assert user_orm.last_login is not None

    @pytest.mark.asyncio
    async def test_update_last_login_nonexistent_returns_false(self, user_repo, mock_db):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = result_mock

        result = await user_repo.update_last_login("ghost")
        assert result is False


# =============================================================================
# Tests de delete_user() (soft-delete)
# =============================================================================

class TestDeleteUser:

    @pytest.mark.asyncio
    async def test_soft_delete_existing_user(self, user_repo, mock_db):
        user_orm = _make_user_orm(username="alice", is_active=True, deleted_at=None)
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = user_orm
        mock_db.execute.return_value = result_mock

        result = await user_repo.delete_user("alice")
        assert result is True
        assert user_orm.is_active is False
        assert user_orm.deleted_at is not None

    @pytest.mark.asyncio
    async def test_soft_delete_nonexistent_returns_false(self, user_repo, mock_db):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = result_mock

        result = await user_repo.delete_user("ghost")
        assert result is False


# =============================================================================
# Tests de list_users()
# =============================================================================

class TestListUsers:

    @pytest.mark.asyncio
    async def test_list_users_returns_list_of_dicts(self, user_repo, mock_db):
        users = [
            _make_user_orm(id=1, username="admin"),
            _make_user_orm(id=2, username="alice"),
        ]
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = users
        result_mock = MagicMock()
        result_mock.scalars.return_value = scalars_mock
        mock_db.execute.return_value = result_mock

        result = await user_repo.list_users()
        assert len(result) == 2
        assert result[0]["username"] == "admin"
        assert result[1]["username"] == "alice"

    @pytest.mark.asyncio
    async def test_list_users_empty(self, user_repo, mock_db):
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        result_mock = MagicMock()
        result_mock.scalars.return_value = scalars_mock
        mock_db.execute.return_value = result_mock

        result = await user_repo.list_users()
        assert result == []


# =============================================================================
# Tests de _to_dict()
# =============================================================================

class TestToDict:

    def test_to_dict_basic_fields(self):
        user_orm = _make_user_orm(
            id=1,
            username="admin",
            email="admin@test.com",
            role="administrateur",
            is_active=True,
        )
        result = UserRepository._to_dict(user_orm)
        assert result["id"] == 1
        assert result["username"] == "admin"
        assert result["email"] == "admin@test.com"
        assert result["role"] == "administrateur"
        assert result["is_active"] is True

    def test_to_dict_last_login_none(self):
        user_orm = _make_user_orm(last_login=None)
        result = UserRepository._to_dict(user_orm)
        assert result["last_login"] is None

    def test_to_dict_last_login_isoformat(self):
        dt = datetime(2026, 6, 27, 10, 0, 0, tzinfo=timezone.utc)
        user_orm = _make_user_orm(last_login=dt)
        result = UserRepository._to_dict(user_orm)
        assert "2026-06-27" in result["last_login"]

    def test_to_dict_perimeter_default_empty_list(self):
        user_orm = _make_user_orm(perimeter=None)
        result = UserRepository._to_dict(user_orm)
        assert result["perimeter"] == []
