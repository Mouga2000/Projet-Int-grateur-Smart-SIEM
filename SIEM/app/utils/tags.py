# app/utils/tags.py
# -------------------------------
# Énumérations : rôles, périmètres, criticité, types de logs

from enum import Enum
from typing import List


# =============================================================================
# 1. RÔLES UTILISATEUR (EX-F-052 à EX-F-056, US-35)
# =============================================================================

class Role(str, Enum):
    """Rôles utilisateur du SIEM. Hérite de str pour la sérialisation Pydantic."""

    LECTEUR = "lecteur"
    """Accès en lecture seule sur un périmètre restreint (ex: stagiaire)."""

    ANALYSTE = "analyste"
    """Consultation, traitement des alertes, marquage. Pas de gestion des utilisateurs."""

    AUDITEUR = "auditeur"
    """Vérification de la conformité (RGPD, ISO 27001), logs d'audit et rapports."""

    RSSI = "rssi"
    """Vue synthétique (KPI), génération de rapports. Pas d'accès aux logs bruts."""

    ADMINISTRATEUR = "administrateur"
    """Gestion complète : utilisateurs, règles, audit, configuration."""

    def get_permissions(self) -> List[str]:
        """Retourne la liste des permissions associées à ce rôle."""
        return ROLE_PERMISSIONS_MAP.get(self, [])

    def is_admin(self) -> bool:
        """Vérifie si le rôle est administrateur (permission globale)."""
        return self == Role.ADMINISTRATEUR


# =============================================================================
# 2. MATRICE DES PERMISSIONS (RBAC)
# =============================================================================

ROLE_PERMISSIONS_MAP: dict[Role, List[str]] = {
    Role.LECTEUR: [
        "read:logs",
        "read:dashboard",
        "read:reports",
    ],
    Role.ANALYSTE: [
        "read:logs",
        "read:dashboard",
        "read:reports",
        "write:alerts",
        "read:incidents",
        "write:incidents",
        "read:audit",
    ],
    Role.AUDITEUR: [
        "read:audit",
        "read:reports",
        "export:data",
    ],
    Role.RSSI: [
        "read:dashboard",
        "read:reports",
        "write:reports",
    ],
    Role.ADMINISTRATEUR: ["*"],  # Toutes les permissions
}


# =============================================================================
# 3. PÉRIMÈTRES FONCTIONNELS (EX-F-061 à EX-F-064)
# =============================================================================

class Perimeter(str, Enum):
    """Périmètre fonctionnel pour la ségrégation des accès."""

    EQUIPE = "equipe"
    """Groupe fonctionnel (ex: équipe réseau, équipe RH)."""

    SERVICE = "service"
    """Unité organisationnelle (ex: DSI, Service Sécurité)."""

    FILIALE = "filiale"
    """Entité juridique ou géographique (ex: Cameroun, France)."""

    ENVIRONNEMENT = "environnement"
    """Contexte technique (ex: production, recette, développement)."""

    @classmethod
    def get_all(cls) -> List[str]:
        """Retourne la liste de tous les périmètres (pour les administrateurs)."""
        return [p.value for p in cls]


# =============================================================================
# 4. CONSTANTES ANNEXES (commentaires-guides)
# =============================================================================

# CRITICITY_TAGS = {
#     "critical": {"color": "red", "priority": 5, "description": "Menace immédiate"},
#     "high": {"color": "orange", "priority": 4, "description": "Menace sérieuse"},
#     "medium": {"color": "yellow", "priority": 3, "description": "Menace potentielle"},
#     "low": {"color": "green", "priority": 2, "description": "Information"},
#     "info": {"color": "blue", "priority": 1, "description": "Simple information"},
# }

# LOG_TYPES = {
#     "authentication": ["login", "logout", "failed_login", "password_change", "mfa"],
#     "network": ["connection", "dns", "dhcp", "firewall", "proxy", "vpn"],
#     "system": ["process", "service", "file", "registry", "scheduled_task"],
#     "application": ["web", "database", "email", "api"],
#     "security": ["antivirus", "ids_ips", "waf", "dlp"],
# }

# SEVERITY_LEVELS = ["debug", "info", "notice", "warning", "error", "critical", "alert", "emergency"]

# SOURCE_TYPES = {
#     "syslog": {"port": 514, "protocol": "udp"},
#     "windows_event": {"port": 5985, "protocol": "http"},
#     "netflow": {"port": 2055, "protocol": "udp"},
#     "json_api": {"port": 443, "protocol": "https"},
# }

# def get_criticity_priority(criticity: str) -> int:
#     """Retourne la priorité numérique d'une criticité."""
#     return CRITICITY_TAGS.get(criticity, {}).get("priority", 0)


# =============================================================================
# 5. EXEMPLES D'UTILISATION
# =============================================================================
#
# from app.utils.tags import Role, Perimeter, ROLE_PERMISSIONS_MAP
#
# # Vérifier les permissions d'un rôle
# role = Role.ANALYSTE
# permissions = role.get_permissions()  # ["read:logs", "read:dashboard", ...]
#
# # Vérifier si admin
# if role.is_admin():
#     print("Accès total")
#
# # Vérifier une permission spécifique dans dependencies.py
# def require_permission(permission: str):
#     async def checker(current_user=Depends(get_current_user)):
#         role = Role(current_user["role"])
#         perms = role.get_permissions()
#         if "*" not in perms and permission not in perms:
#             raise HTTPException(status_code=403)
#         return True
#     return checker
#
# # Périmètres : filtrer les accès
# perimeter = Perimeter.EQUIPE
# all_perimeters = Perimeter.get_all()
