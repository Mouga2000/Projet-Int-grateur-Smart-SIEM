# app/utils/validators.py
# -------------------------------
# Fonctions de validation
#
# Ce que tu dois mettre ici :
#
#   import ipaddress
#   import re
#   from typing import Union
#
#   def validate_ip(ip: str) -> bool:
#       """Vérifie si une chaîne est une IP valide (v4 ou v6)."""
#       try:
#           ipaddress.ip_address(ip)
#           return True
#       except ValueError:
#           return False
#
#   def validate_domain(domain: str) -> bool:
#       """Vérifie si un domaine est valide."""
#       pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
#       return bool(re.match(pattern, domain))
#
#   def validate_hash(hash_str: str, algorithm: str = "sha256") -> bool:
#       """Vérifie la longueur d'un hash selon l'algorithme."""
#       lengths = {"md5": 32, "sha1": 40, "sha256": 64, "sha512": 128}
#       return len(hash_str) == lengths.get(algorithm, 64)
#
#   def validate_port(port: Union[int, str]) -> bool:
#       """Vérifie si un port est dans la plage valide (1-65535)."""
#       try:
#           return 1 <= int(port) <= 65535
#       except (ValueError, TypeError):
#           return False
#
#   def sanitize_log_field(value: str) -> str:
#       """Nettoie un champ de log pour éviter les injections ES."""
#       # Supprime les caractères de contrôle
#       return re.sub(r"[\x00-\x1f\x7f]", "", value)
