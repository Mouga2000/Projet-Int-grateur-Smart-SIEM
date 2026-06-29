# app/tests/test_repositories/test_notification_repo.py
# -------------------------------
# Tests unitaires du repository Notification (app/repositories/notification_repo.py)

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.repositories.notification_repo import NotificationRepository


@pytest.fixture
def db_session():
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def notif_repo(db_session):
    return NotificationRepository(db_session)


class TestNotificationCreate:
    @pytest.mark.asyncio
    async def test_create_in_app(self, notif_repo, db_session):
        from app.models.sql_models import Notification
        mock_notif = MagicMock()
        mock_notif.id = 1
        mock_notif.user_id = 1
        mock_notif.title = "Test"
        mock_notif.message = "Hello"
        mock_notif.channel = "in_app"
        mock_notif.is_read = False
        mock_notif.read_at = None
        mock_notif.created_at = MagicMock()
        db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))

        with patch("app.repositories.notification_repo.Notification", return_value=mock_notif):
            result = await notif_repo.create(1, "Test", "Hello", channel="in_app")
            assert result["id"] == 1
            assert result["channel"] == "in_app"


class TestGetUserNotifications:
    @pytest.mark.asyncio
    async def test_get_all(self, notif_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db_session.execute.return_value = result_mock
        items = await notif_repo.get_user_notifications(1)
        assert items == []

    @pytest.mark.asyncio
    async def test_get_unread_only(self, notif_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        db_session.execute.return_value = result_mock
        items = await notif_repo.get_user_notifications(1, unread_only=True)
        assert items == []


class TestMarkAsRead:
    @pytest.mark.asyncio
    async def test_mark_as_read(self, notif_repo, db_session):
        from app.models.sql_models import Notification
        mock_notif = MagicMock()
        mock_notif.is_read = False
        mock_notif.read_at = None
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_notif
        db_session.execute.return_value = result_mock

        result = await notif_repo.mark_as_read(1, user_id=1)
        assert result is True
        assert mock_notif.is_read is True

    @pytest.mark.asyncio
    async def test_mark_as_read_nonexistent(self, notif_repo, db_session):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db_session.execute.return_value = result_mock
        result = await notif_repo.mark_as_read(999, user_id=1)
        assert result is False


class TestMarkAllAsRead:
    @pytest.mark.asyncio
    async def test_mark_all_read(self, notif_repo, db_session):
        from app.models.sql_models import Notification
        mock1, mock2 = MagicMock(spec=Notification), MagicMock(spec=Notification)
        mock1.is_read = False
        mock2.is_read = False
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [mock1, mock2]
        db_session.execute.return_value = result_mock

        count = await notif_repo.mark_all_as_read(1)
        assert count == 2
        assert mock1.is_read is True
        assert mock2.is_read is True


class TestCountUnread:
    @pytest.mark.asyncio
    async def test_count_unread(self, notif_repo, db_session):
        from app.models.sql_models import Notification
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [MagicMock(), MagicMock(), MagicMock()]
        db_session.execute.return_value = result_mock

        count = await notif_repo.count_unread(1)
        assert count == 3
