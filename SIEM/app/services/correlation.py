# ==========================================================
# FICHIER : app/services/correlation.py
# ==========================================================
# Ce fichier contient le moteur de corrélation du SIEM.
#
# Son rôle est de :
# 1. Recevoir un log déjà normalisé.
# 2. Charger toutes les règles de détection.
# 3. Tester le log avec chaque règle.
# 4. Déterminer si une menace est détectée.
# 5. Créer une alerte.
# 6. Déclencher automatiquement le SOAR si nécessaire.
# ==========================================================


# ----------------------------------------------------------
# Importation des types Dict et List.
#
# Dict représente un dictionnaire Python.
#
# Exemple :
# {
#     "source_ip": "192.168.1.15",
#     "event_type": "login_failed"
# }
#
# List représente une liste.
#
# Exemple :
# [
#     règle1,
#     règle2,
#     règle3
# ]
# ----------------------------------------------------------
from typing import Dict, List


# ----------------------------------------------------------
# Déclaration de la classe CorrelationEngine.
#
# Cette classe représente le moteur de corrélation du SIEM.
#
# C'est elle qui décide si un événement est dangereux.
# ----------------------------------------------------------
class CorrelationEngine:

    """
    ======================================================
    Documentation de la classe.

    Ce moteur reçoit les logs déjà normalisés.

    Ensuite il applique toutes les règles de sécurité.

    Lorsqu'une règle est satisfaite,
    une alerte est créée automatiquement.

    Il peut également lancer un playbook SOAR.

    Cette documentation est uniquement destinée
    aux développeurs.
    ======================================================
    """


    # ------------------------------------------------------
    # Constructeur de la classe.
    #
    # Il est exécuté automatiquement lorsqu'on crée
    # un objet CorrelationEngine.
    #
    # Exemple :
    #
    # engine = CorrelationEngine(...)
    #
    # Les différents repositories sont injectés
    # afin que cette classe puisse communiquer
    # avec les autres composants.
    # ------------------------------------------------------
    def __init__(
        self,

        # Repository contenant toutes les règles
        # de corrélation.
        rule_repository,

        # Repository chargé des alertes.
        alert_repository,

        # Repository Elasticsearch.
        elastic_repository,

        # Client Redis.
        redis_client,

        # Service SOAR.
        # Il est facultatif.
        soar_service=None,
    ):

        # Sauvegarde du repository des règles
        # dans l'objet courant.
        self.rule_repository = rule_repository

        # Sauvegarde du repository des alertes.
        self.alert_repository = alert_repository

        # Sauvegarde du repository Elasticsearch.
        self.elastic_repository = elastic_repository

        # Sauvegarde du client Redis.
        self.redis = redis_client

        # Sauvegarde du service SOAR.
        self.soar = soar_service


    # ------------------------------------------------------
    # Fonction principale du moteur.
    #
    # Elle est appelée chaque fois
    # qu'un nouveau log arrive.
    #
    # async signifie que la fonction
    # est asynchrone.
    # ------------------------------------------------------
    async def evaluate_event(self, normalized_log: Dict):

        """
        Point d'entrée principal du moteur.

        Toute l'analyse commence ici.
        """

        # --------------------------------------------------
        # On demande au repository
        # toutes les règles actives.
        #
        # await signifie :
        #
        # "attendre la réponse avant de continuer".
        # --------------------------------------------------
        rules = await self.rule_repository.get_enabled_rules()


        # --------------------------------------------------
        # Parcours de toutes les règles.
        #
        # Chaque règle est testée indépendamment.
        # --------------------------------------------------
        for rule in rules:


            # ------------------------------------------------
            # Au départ aucune menace n'est détectée.
            # ------------------------------------------------
            detected = False


            # ------------------------------------------------
            # Vérifie si la règle concerne
            # un seul événement.
            # ------------------------------------------------
            if rule["type"] == "single_event":

                # Exécution du test.
                detected = await self.check_single_event_rule(

                    # La règle courante.
                    rule,

                    # Le log reçu.
                    normalized_log,
                )


            # ------------------------------------------------
            # Vérifie si la règle est une règle de seuil.
            # ------------------------------------------------
            elif rule["type"] == "threshold":

                detected = await self.check_threshold_rule(

                    rule,

                    normalized_log,
                )


            # ------------------------------------------------
            # Vérifie une corrélation
            # entre plusieurs événements.
            # ------------------------------------------------
            elif rule["type"] == "correlation":

                detected = await self.check_correlation_rule(

                    rule,

                    normalized_log,
                )


            # ------------------------------------------------
            # Vérifie une séquence d'événements.
            # ------------------------------------------------
            elif rule["type"] == "sequence":

                detected = await self.check_sequence_rule(

                    rule,

                    normalized_log,
                )


            # ------------------------------------------------
            # Si une menace est détectée,
            # on crée une alerte.
            # ------------------------------------------------
            if detected:

                await self.create_alert(

                    rule,

                    normalized_log,
                )


    # ------------------------------------------------------
    # Vérification d'une règle simple.
    #
    # Une seule condition suffit.
    # ------------------------------------------------------
    async def check_single_event_rule(

        self,

        # La règle.
        rule: Dict,

        # Le log.
        log: Dict,

    ) -> bool:

        """
        Vérifie une règle portant
        sur un seul événement.
        """

        # --------------------------------------------------
        # Extraction de la condition.
        #
        # Exemple :
        #
        # {
        #     "field": "event_type",
        #     "value": "login_failed"
        # }
        # --------------------------------------------------
        condition = rule["condition"]


        # --------------------------------------------------
        # Comparaison entre
        # la valeur du log
        # et la valeur attendue.
        #
        # Si elles sont identiques :
        #
        # True
        #
        # Sinon :
        #
        # False
        # --------------------------------------------------
        return (

            log.get(condition["field"])

            ==

            condition["value"]

        )


    # ------------------------------------------------------
    # Vérification d'une règle de seuil.
    # ------------------------------------------------------
    async def check_threshold_rule(

        self,

        rule: Dict,

        log: Dict,

    ) -> bool:

        """
        Détection par seuil.

        Exemple :

        5 échecs de connexion

        en moins de 60 secondes.
        """

        # --------------------------------------------------
        # Ici Redis est utilisé.
        #
        # Redis incrémente un compteur.
        #
        # Exemple :
        #
        # login_failed:192.168.1.10
        #
        # Valeur :
        #
        # 1
        #
        # puis
        #
        # 2
        #
        # puis
        #
        # 3
        # --------------------------------------------------


        # --------------------------------------------------
        # Redis ajoute également un TTL.
        #
        # Exemple :
        #
        # 60 secondes.
        #
        # Après 60 secondes,
        # le compteur disparaît automatiquement.
        # --------------------------------------------------


        # --------------------------------------------------
        # Ensuite le moteur lit
        # la valeur actuelle du compteur.
        # --------------------------------------------------


        # --------------------------------------------------
        # Si le seuil est atteint,
        #
        # True
        #
        # Sinon
        #
        # False
        # --------------------------------------------------
        pass


    # ------------------------------------------------------
    # Corrélation entre plusieurs sources.
    # ------------------------------------------------------
    async def check_correlation_rule(

        self,

        rule: Dict,

        log: Dict,

    ) -> bool:

        """
        Corrélation entre plusieurs sources.

        Exemple :

        Firewall

              +

        Active Directory

              +

        Endpoint
        """

        # --------------------------------------------------
        # Elasticsearch est interrogé.
        #
        # Il recherche tous les événements liés
        # à cette adresse IP,
        # cet utilisateur
        # ou cette machine.
        # --------------------------------------------------


        # --------------------------------------------------
        # Ensuite les événements sont comparés.
        #
        # Si la combinaison correspond
        # à la règle,
        #
        # True
        #
        # Sinon
        #
        # False
        # --------------------------------------------------
        pass


    # ------------------------------------------------------
    # Vérification d'une séquence.
    # ------------------------------------------------------
    async def check_sequence_rule(

        self,

        rule: Dict,

        log: Dict,

    ) -> bool:

        """
        Détection de séquences.

        Exemple :

        Login Failed

        →

        Login Success

        →

        Exécution PowerShell
        """

        # --------------------------------------------------
        # Redis mémorise
        # l'étape atteinte.
        #
        # Exemple :
        #
        # Étape 1
        #
        # puis
        #
        # Étape 2
        #
        # puis
        #
        # Étape 3
        # --------------------------------------------------


        # --------------------------------------------------
        # Lorsque toutes les étapes
        # sont réalisées
        # dans le bon ordre,
        #
        # True
        #
        # est retourné.
        # --------------------------------------------------
        pass


    # ------------------------------------------------------
    # Création d'une alerte.
    # ------------------------------------------------------
    async def create_alert(

        self,

        rule: Dict,

        log: Dict,

    ):

        """
        Génère une alerte.

        Étape 1 :
        Sauvegarde dans PostgreSQL.

        Étape 2 :
        Déclenchement du SOAR.

        Étape 3 :
        Retourne l'identifiant de l'alerte.
        """

        # --------------------------------------------------
        # Construction du dictionnaire
        # représentant l'alerte.
        # --------------------------------------------------
        alert = {

            # Identifiant de la règle.
            "rule_id": rule["id"],

            # Nom de la règle.
            "rule_name": rule["name"],

            # Niveau de gravité.
            "severity": rule["severity"],

            # Adresse IP source.
            "source_ip": log.get("source_ip"),

            # Type d'événement.
            "event_type": log.get("event_type"),

            # Date et heure.
            "timestamp": log.get("timestamp"),

            # Description de la menace.
            "description": rule["description"],

            # Tactique MITRE ATT&CK.
            "mitre_tactic": rule.get("mitre_tactic"),

            # Technique MITRE ATT&CK.
            "mitre_technique": rule.get("mitre_technique"),
        }


        # --------------------------------------------------
        # Sauvegarde de l'alerte
        # dans PostgreSQL.
        #
        # La base retourne
        # l'identifiant créé.
        # --------------------------------------------------
        alert_id = await self.alert_repository.create(alert)


        # --------------------------------------------------
        # Vérifie si un SOAR est configuré.
        # --------------------------------------------------
        if self.soar:

            # Déclenche automatiquement
            # le playbook SOAR.
            await self.soar.execute_playbook(

                # Identifiant de l'alerte.
                alert_id,

                # Règle ayant déclenché l'alerte.
                rule,

                # Log responsable de l'alerte.
                log,
            )


        # --------------------------------------------------
        # Retourne l'identifiant
        # de l'alerte créée.
        # --------------------------------------------------
        return alert_id