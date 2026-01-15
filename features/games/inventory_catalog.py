"""
features/inventory_catalog.py

Inventory definition access boundary.

Responsibilities:
- Provide access to FOOD_DEF / SOAP_DEF / POTION_DEF via an injectable abstraction.
- Preserve existing dict shapes and keys (no gameplay changes).

Collaboration:
- Used by `features.game.Game` and view helpers to avoid direct module-global coupling.
"""

from __future__ import annotations

from typing import Dict, Protocol

from constants.configs import FOOD_DEF, SOAP_DEF, POTION_DEF


class InventoryCatalog(Protocol):
    """Abstraction for accessing item definition mappings."""
    def food_defs(self) -> Dict: ...
    def soap_defs(self) -> Dict: ...
    def potion_defs(self) -> Dict: ...


class DefaultInventoryCatalog:
    """Default catalog that returns the existing constant dicts unchanged."""
    def food_defs(self) -> Dict:
        return FOOD_DEF

    def soap_defs(self) -> Dict:
        return SOAP_DEF

    def potion_defs(self) -> Dict:
        return POTION_DEF