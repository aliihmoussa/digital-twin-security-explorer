from __future__ import annotations

from typing import Any

import streamlit as st

KEY_NAV = "nav_page"
KEY_PENDING_NAV = "_pending_nav_page"
KEY_PENDING_PROP = "_pending_f_prop"


def init_state(bundle: dict[str, Any]) -> None:
    if "layer_key" not in st.session_state:
        st.session_state.layer_key = "layer1"
    if "attack_id" not in st.session_state:
        st.session_state.attack_id = bundle["flat_attacks"][0]["id"]
    if "compare_ids" not in st.session_state:
        st.session_state.compare_ids = []
    if KEY_NAV not in st.session_state:
        st.session_state[KEY_NAV] = "Explore"
    qp = st.query_params
    if "attack" in qp:
        aid = str(qp.get("attack", ""))
        if aid in bundle["attack_by_id"]:
            st.session_state.attack_id = aid
            st.session_state.layer_key = bundle["attack_by_id"][aid]["layer_key"]


def apply_pending_nav() -> None:
    if KEY_PENDING_NAV in st.session_state:
        st.session_state[KEY_NAV] = st.session_state.pop(KEY_PENDING_NAV)


def apply_pending_property() -> None:
    if KEY_PENDING_PROP in st.session_state:
        st.session_state.f_prop = st.session_state.pop(KEY_PENDING_PROP)
