import pytest
from app.services.correlation import CorrelationEngine

# ==========================================================
# Fake Repository des règles
# ==========================================================
class FakeRuleRepository:
    async def get_enabled_rules(self):
        return [
            {
                "id": 1,
                "name": "Login Failed Rule",
                "type": "single_event",
                "severity": "high",
                "condition": {
                    "field": "event_type",
                    "value": "login_failed"
                },
                "description": "Détection d'un échec de connexion"
            }
        ]


# ==========================================================
# Fake Repository des alertes
# ==========================================================
class FakeAlertRepository:

    def __init__(self):
        self.created = False
        self.saved_alert = None

    async def create(self, alert):
        self.created = True
        self.saved_alert = alert

        print("\n================ ALERTE CRÉÉE ================")
        print(alert)
        print("==============================================\n")

        return 1001


# ==========================================================
# Création des faux objets
# ==========================================================
alert_repository = FakeAlertRepository()

engine = CorrelationEngine(
    rule_repository=FakeRuleRepository(),
    alert_repository=alert_repository,
    elastic_repository=None,
    redis_client=None,
    soar_service=None
)


# ==========================================================
# Test unitaire
# ==========================================================
@pytest.mark.asyncio
async def test_single_event_detection():

    # Log simulé reçu par le SIEM
    test_log = {
        "source_ip": "192.168.1.10",
        "event_type": "login_failed",
        "timestamp": "2026-06-27T10:00:00Z"
    }

    # Exécution du moteur de corrélation
    await engine.evaluate_event(test_log)

    # Vérifications
    assert alert_repository.created is True
    assert alert_repository.saved_alert is not None
    assert alert_repository.saved_alert["event_type"] == "login_failed"
    assert alert_repository.saved_alert["severity"] == "high"