# app/tests/test_utils_tags.py
# -------------------------------
# Tests des énumérations Role et Perimeter

import pytest
from app.utils.tags import Role, Perimeter, ROLE_PERMISSIONS_MAP


class TestRole:

    def test_role_values(self):
        assert Role.LECTEUR == "lecteur"
        assert Role.ANALYSTE == "analyste"
        assert Role.AUDITEUR == "auditeur"
        assert Role.RSSI == "rssi"
        assert Role.ADMINISTRATEUR == "administrateur"

    def test_role_count(self):
        assert len(Role) == 5

    def test_role_from_string(self):
        assert Role("lecteur") == Role.LECTEUR
        assert Role("administrateur") == Role.ADMINISTRATEUR

    def test_invalid_role_raises_error(self):
        with pytest.raises(ValueError):
            Role("superadmin")

    def test_get_permissions_lecteur(self):
        perms = Role.LECTEUR.get_permissions()
        assert "read:logs" in perms
        assert "read:dashboard" in perms
        assert "read:reports" in perms
        assert "*" not in perms

    def test_get_permissions_analyste(self):
        perms = Role.ANALYSTE.get_permissions()
        assert "write:alerts" in perms
        assert "read:incidents" in perms

    def test_get_permissions_auditeur(self):
        perms = Role.AUDITEUR.get_permissions()
        assert "read:audit" in perms
        assert "export:data" in perms

    def test_get_permissions_rssi(self):
        perms = Role.RSSI.get_permissions()
        assert "write:reports" in perms
        assert "read:logs" not in perms  # Le RSSI n'a pas accès aux logs bruts

    def test_get_permissions_admin(self):
        perms = Role.ADMINISTRATEUR.get_permissions()
        assert perms == ["*"]

    def test_is_admin(self):
        assert Role.ADMINISTRATEUR.is_admin() is True
        assert Role.ANALYSTE.is_admin() is False
        assert Role.LECTEUR.is_admin() is False

    def test_role_str_comparison(self):
        """Role hérite de str, donc la comparaison avec une string fonctionne."""
        assert Role.ADMINISTRATEUR == "administrateur"
        assert "analyste" == Role.ANALYSTE


class TestPerimeter:

    def test_perimeter_values(self):
        assert Perimeter.EQUIPE == "equipe"
        assert Perimeter.SERVICE == "service"
        assert Perimeter.FILIALE == "filiale"
        assert Perimeter.ENVIRONNEMENT == "environnement"

    def test_perimeter_count(self):
        assert len(Perimeter) == 4

    def test_get_all(self):
        all_p = Perimeter.get_all()
        assert len(all_p) == 4
        assert "equipe" in all_p
        assert "environnement" in all_p

    def test_perimeter_str_comparison(self):
        assert Perimeter.EQUIPE == "equipe"


class TestRolePermissionsMap:

    def test_all_roles_in_map(self):
        for role in Role:
            assert role in ROLE_PERMISSIONS_MAP

    def test_admin_has_wildcard(self):
        assert ROLE_PERMISSIONS_MAP[Role.ADMINISTRATEUR] == ["*"]

    def test_analyste_can_write_alerts(self):
        assert "write:alerts" in ROLE_PERMISSIONS_MAP[Role.ANALYSTE]


class TestStatutIncident:

    def test_statut_values(self):
        from app.utils.tags import StatutIncident
        assert StatutIncident.OUVERTE == "ouverte"
        assert StatutIncident.EN_COURS == "en_cours"
        assert StatutIncident.RESOLUE == "resolue"
        assert StatutIncident.CLOTUREE == "cloturee"

    def test_statut_count(self):
        from app.utils.tags import StatutIncident
        assert len(StatutIncident) == 4

    def test_statut_from_string(self):
        from app.utils.tags import StatutIncident
        assert StatutIncident("ouverte") == StatutIncident.OUVERTE
        assert StatutIncident("cloturee") == StatutIncident.CLOTUREE


class TestNiveauAlerte:

    def test_niveau_values(self):
        from app.utils.tags import NiveauAlerte
        assert NiveauAlerte.INFO == "info"
        assert NiveauAlerte.LOW == "low"
        assert NiveauAlerte.MEDIUM == "medium"
        assert NiveauAlerte.HIGH == "high"
        assert NiveauAlerte.CRITICAL == "critical"

    def test_niveau_count(self):
        from app.utils.tags import NiveauAlerte
        assert len(NiveauAlerte) == 5

    def test_niveau_from_string(self):
        from app.utils.tags import NiveauAlerte
        assert NiveauAlerte("critical") == NiveauAlerte.CRITICAL
        assert NiveauAlerte("info") == NiveauAlerte.INFO
