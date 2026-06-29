# app/tests/test_services/test_soar.py
# -------------------------------
# Tests unitaires du service SOAR (app/services/soar.py)

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.soar import SOARService


@pytest.fixture
def playbook_repo():
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    repo.increment_execution = AsyncMock()
    return repo


@pytest.fixture
def soar(playbook_repo):
    return SOARService(playbook_repo)


class TestExecuteStep:
    """Tests des actions individuelles d'un playbook."""

    @pytest.mark.asyncio
    async def test_block_ip_no_agent(self, soar):
        step = {"action": "block_ip", "params": {}}
        result = await soar.execute_step(step, {})
        assert result["success"] is False
        assert "agent manquante" in result.get("error", "")

    @pytest.mark.asyncio
    async def test_block_ip(self, soar):
        context = {"source_ip": "10.0.0.5", "host": "192.168.1.1"}
        step = {"action": "block_ip", "params": {}}
        with patch("httpx.AsyncClient") as mock_client:
            mock_post = AsyncMock()
            mock_post.return_value = MagicMock(status_code=200, json=lambda: {"success": True})
            mock_client.return_value.__aenter__.return_value.post = mock_post
            result = await soar.execute_step(step, context)
            assert result is not None
            assert "success" in result

    @pytest.mark.asyncio
    async def test_disable_user(self, soar):
        context = {"host": "192.168.1.1", "user": "john"}
        step = {"action": "disable_user", "params": {}}
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=MagicMock(status_code=200, json=lambda: {"success": True})
            )
            result = await soar.execute_step(step, context)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_isolate_host(self, soar):
        context = {"host": "192.168.1.1"}
        step = {"action": "isolate_host", "params": {}}
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=MagicMock(status_code=200, json=lambda: {"success": True})
            )
            result = await soar.execute_step(step, context)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_notify_slack(self, soar):
        step = {"action": "notify_slack", "params": {"channel": "#sec", "message": "test"}}
        with patch("app.services.soar.send_slack_notification.delay") as mock_slack:
            result = await soar.execute_step(step, {})
            assert result["success"] is True
            mock_slack.assert_called_once_with("#sec", "test")

    @pytest.mark.asyncio
    async def test_notify_email(self, soar):
        step = {"action": "notify_email", "params": {"to": "admin@test.com", "subject": "Alert", "body": "Test"}}
        with patch("app.services.soar.send_email_notification.delay") as mock_email:
            result = await soar.execute_step(step, {})
            assert result["success"] is True
            mock_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_ticket(self, soar):
        step = {"action": "create_ticket", "params": {"title": "Incident #1"}}
        result = await soar.execute_step(step, {})
        assert result["success"] is True
        assert "ticket_id" in result
        assert result["ticket_id"].startswith("SIEM-")

    @pytest.mark.asyncio
    async def test_unknown_action(self, soar):
        step = {"action": "do_nothing", "params": {}}
        result = await soar.execute_step(step, {})
        assert result["success"] is False
        assert "inconnue" in result.get("error", "")

    @pytest.mark.asyncio
    async def test_agent_unreachable(self, soar):
        context = {"host": "192.168.1.1"}
        step = {"action": "block_ip", "params": {"ip": "10.0.0.5"}}
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=Exception("Connection refused")
            )
            result = await soar.execute_step(step, context)
            assert result["success"] is False


class TestExecutePlaybook:
    """Tests d'exécution d'un playbook complet."""

    @pytest.mark.asyncio
    async def test_execute_full_playbook(self, soar, playbook_repo):
        playbook_repo.get_by_id.return_value = {
            "name": "Block malicious IP",
            "steps": [
                {"action": "notify_slack", "params": {"channel": "#sec", "message": "IP bloquee"}},
            ],
            "max_retries": 0,
        }
        context = {"source_ip": "10.0.0.5", "host": "192.168.1.1"}
        with patch("app.services.soar.send_slack_notification.delay"):
            result = await soar.execute_playbook(1, context)
            assert result["success"] is True
            assert result["playbook"] == "Block malicious IP"

    @pytest.mark.asyncio
    async def test_playbook_not_found(self, soar, playbook_repo):
        playbook_repo.get_by_id.return_value = None
        result = await soar.execute_playbook(999, {})
        assert result["success"] is False
        assert "non trouve" in result.get("error", "")
