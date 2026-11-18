"""Bridge OpenGrid model elements to the existing QElectroTech asset catalog.

This checks identity and declared port domains. It does NOT claim a drawing
symbol represents an electrically verified installation.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schema import Project

# These are references to assets/catalog.json, not substitute electrical ratings.
SYMBOL_BY_COLLECTION = {
    "source": "utility",
    "buses": "bus",
    "loads": "load_panel",
    "pv": "pv_inverter",
    "batteries": "power_conversion_system",
}


def read_catalog(path: Path) -> dict[str, dict[str, Any]]:
    """Load a reusable symbol catalog, rejecting duplicate or malformed IDs."""
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    symbols = document.get("symbols")
    if not isinstance(symbols, list):
        raise ValueError("Asset catalog must contain a symbols array")
    lookup: dict[str, dict[str, Any]] = {}
    for item in symbols:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("Catalog symbol lacks a string id")
        if item["id"] in lookup:
            raise ValueError(f"Duplicate catalog symbol id: {item['id']}")
        lookup[item["id"]] = item
    return lookup


def audit_catalog(project: Project, catalog_path: Path) -> dict[str, Any]:
    """Report symbol coverage and AC port contracts without modifying models."""
    symbols = read_catalog(catalog_path)
    mapped = []
    for collection, symbol_id in SYMBOL_BY_COLLECTION.items():
        objects = [project.source] if collection == "source" else getattr(project, collection)
        for obj in objects:
            symbol = symbols.get(symbol_id)
            if symbol is None:
                raise ValueError(f"Missing required symbol: {symbol_id} for {obj.id}")
            ports = symbol.get("ports", [])
            if not any(isinstance(port, dict) and port.get("domain") == "ac" for port in ports):
                raise ValueError(f"Symbol {symbol_id} has no AC-domain port")
            mapped.append({"equipment_id": obj.id, "symbol_id": symbol_id,
                           "domain": "ac", "symbol_family": symbol.get("family")})
    # Neither a cable nor wind turbine is represented as a standard QET symbol here.
    # A generator-set symbol is not a safe substitute for a wind turbine.
    missing = ([{"kind": "wind_turbine", "count": len(project.wind)}]
               if project.wind else [])
    return {"catalog": str(catalog_path), "catalog_symbols": len(symbols),
            "mapped": mapped, "unmapped": missing,
            "note": "Catalog mapping is schematic identity only, not design verification"}
