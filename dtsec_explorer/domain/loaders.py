from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .transforms import enrich_properties, enrich_technologies, flatten_attacks


def data_dir() -> Path:
    env = os.environ.get("DTSEC_DATA_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2] / "document_references"


def _read_json(name: str) -> Any:
    path = data_dir() / name
    if not path.is_file():
        raise FileNotFoundError(f"Missing data file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_all() -> dict[str, Any]:
    attacks_root = _read_json("attacks.json")
    tech_doc = _read_json("technologies.json")
    prop_doc = _read_json("properties.json")
    glossary = _read_json("sfr_glossary.json")

    flat = flatten_attacks(attacks_root)
    technologies = enrich_technologies(attacks_root, tech_doc["technologies"])
    properties = enrich_properties(flat, prop_doc["properties"])

    return {
        "attacks_root": attacks_root,
        "flat_attacks": flat,
        "technologies": technologies,
        "properties": properties,
        "property_by_name": {p["name"]: p for p in properties},
        "sfr_glossary": glossary,
        "attack_by_id": {a["id"]: a for a in flat},
    }
