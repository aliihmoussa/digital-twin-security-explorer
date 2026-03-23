from __future__ import annotations

import re
from typing import Any


def parse_cascade_target_layers(cascade_text: str) -> list[int]:
    return [int(x) for x in re.findall(r"Layer\s*(\d)", cascade_text, flags=re.I)]


def build_cascade_sankey(flat_attacks: list[dict[str, Any]]) -> tuple[list[str], list[int], list[int], list[int]]:
    labels = ["Physical (L1)", "Intermediate (L2)", "Digital (L3)"]
    layer_to_idx = {"layer1": 0, "layer2": 1, "layer3": 2}
    src: list[int] = []
    tgt: list[int] = []
    val: list[int] = []
    flow: dict[tuple[int, int], int] = {}

    for attack in flat_attacks:
        sidx = layer_to_idx[attack["layer_key"]]
        target_indices: set[int] = set()
        for ce in attack.get("cascade_effects", []):
            for n in parse_cascade_target_layers(ce):
                tidx = n - 1
                if 0 <= tidx <= 2 and tidx != sidx:
                    target_indices.add(tidx)
            if "Complete DT failure" in ce and sidx < 2:
                target_indices.add(2)
        for tidx in target_indices:
            key = (sidx, tidx)
            flow[key] = flow.get(key, 0) + 1

    for (s, t), v in sorted(flow.items()):
        src.append(s)
        tgt.append(t)
        val.append(v)

    return labels, src, tgt, val


def cascade_layer_badges(text: str) -> str:
    out = text
    for n, label in ((1, "L1"), (2, "L2"), (3, "L3")):
        out = out.replace(f"Layer {n}", f"**{label}** - Layer {n}")
    return out
