from __future__ import annotations

from copy import deepcopy
from typing import Any

from .constants import LAYER_KEYS, SEVERITY_ORDER


def flatten_attacks(attacks_root: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lk in LAYER_KEYS:
        layer = attacks_root[lk]
        for attack in layer["attacks"]:
            rows.append(
                {
                    **attack,
                    "layer_key": lk,
                    "layer_name": layer["name"],
                    "layer_description": layer["description"],
                    "layer_color": layer["color"],
                }
            )
    return rows


def enrich_technologies(attacks_root: dict[str, Any], technologies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    et_map: dict[str, set[str]] = {t["id"]: set() for t in technologies}
    for lk in LAYER_KEYS:
        for attack in attacks_root[lk]["attacks"]:
            for et in attack.get("enabling_tech", []):
                if et in et_map:
                    et_map[et].add(attack["id"])
    out = deepcopy(technologies)
    for tech in out:
        tech["attacks_defended"] = sorted(et_map.get(tech["id"], set()))
    return out


def enrich_properties(flat_attacks: list[dict[str, Any]], properties: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prop_sfrs: dict[str, set[str]] = {p["name"]: set() for p in properties}
    for attack in flat_attacks:
        for prop in attack.get("security_properties", []):
            if prop in prop_sfrs:
                prop_sfrs[prop].update(attack.get("sfrs", []))

    out = deepcopy(properties)
    for prop in out:
        merged = set(prop.get("sfrs") or []) | prop_sfrs.get(prop["name"], set())
        prop["sfrs"] = sorted(merged)
    return out


def filter_attacks(
    flat_attacks: list[dict[str, Any]],
    layer_key: str | None,
    security_property: str | None,
    severities: list[str],
    query: str,
) -> list[dict[str, Any]]:
    q = (query or "").strip().lower()
    out: list[dict[str, Any]] = []
    for attack in flat_attacks:
        if layer_key and attack["layer_key"] != layer_key:
            continue
        if security_property and security_property != "All" and security_property not in attack.get("security_properties", []):
            continue
        if severities and attack.get("severity") not in severities:
            continue
        if q:
            blob = f"{attack['id']} {attack['name']} {attack['description']}".lower()
            if q not in blob:
                continue
        out.append(attack)

    out.sort(key=lambda item: (SEVERITY_ORDER.get(item["severity"], 9), item["id"]))
    return out
