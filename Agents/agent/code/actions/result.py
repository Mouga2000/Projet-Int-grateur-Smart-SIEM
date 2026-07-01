"""
Résultat d'une action exécutée.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ActionResult:

    success: bool

    message: str = ""

    data: Any = None

    error: str = ""