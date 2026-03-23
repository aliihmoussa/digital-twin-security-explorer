from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from dtsec_explorer.domain import LAYER_KEYS


def render(bundle: dict[str, Any]) -> None:
    st.subheader("Cheat sheet — all 53 attacks")
    for lk in LAYER_KEYS:
        layer = bundle["attacks_root"][lk]
        st.markdown(f"### {layer['name']}")
        rows: list[dict[str, str]] = []
        for attack in layer["attacks"]:
            rows.append(
                {
                    "ID": attack["id"],
                    "Name": attack["name"],
                    "Severity": attack["severity"],
                    "Properties": ", ".join(attack.get("security_properties", [])),
                    "Tech": ", ".join(attack.get("enabling_tech", [])),
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
