from __future__ import annotations

from typing import Any

import streamlit as st

from dtsec_explorer.presentation.state import KEY_PENDING_NAV


def render(bundle: dict[str, Any]) -> None:
    st.subheader("Enabling technologies (ET 1–8)")
    st.caption("From the survey: defensive mechanisms mapped to attacks via `enabling_tech` in attacks.json.")
    techs = bundle["technologies"]
    labels = [f"{t['id']}: {t['name']}" for t in techs]
    choice = st.selectbox("Select technology", range(len(labels)), format_func=lambda i: labels[i])
    tech = techs[choice]

    st.markdown(f"### {tech['name']}")
    st.markdown(tech["description"])
    st.markdown("**Security properties:** " + ", ".join(tech.get("security_properties", [])))
    st.markdown("**Representative SFRs:** " + ", ".join(f"`{s}`" for s in tech.get("sfrs", [])))
    st.markdown(f"**Defends {len(tech.get('attacks_defended', []))} attacks** (where this ET appears in `enabling_tech`)")

    defended = tech.get("attacks_defended", [])
    cols = st.columns(4)
    for i, aid in enumerate(defended[:48]):
        with cols[i % 4]:
            if st.button(aid, key=f"td_{tech['id']}_{aid}"):
                st.session_state.attack_id = aid
                st.session_state.layer_key = bundle["attack_by_id"][aid]["layer_key"]
                st.query_params["attack"] = aid
                st.session_state[KEY_PENDING_NAV] = "Explore"
                st.rerun()

    if len(defended) > 48:
        st.caption("Showing first 48 attack links; full list in export if needed.")
