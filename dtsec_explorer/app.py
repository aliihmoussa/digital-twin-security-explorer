"""DTSec-Explorer — Streamlit entrypoint (thin router)."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# When Streamlit runs a file path (e.g. `streamlit run dtsec_explorer/app.py`),
# the package root may not be on sys.path in some environments (e.g. Streamlit Cloud).
# Ensure repo root is importable so `dtsec_explorer.*` absolute imports always work.
if __package__ in (None, ""):
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

from dtsec_explorer.domain import load_all
from dtsec_explorer.presentation.pages.cheat_sheet import render as render_cheat_sheet
from dtsec_explorer.presentation.pages.explore import render as render_explore
from dtsec_explorer.presentation.pages.technologies import render as render_technologies
from dtsec_explorer.presentation.state import KEY_NAV, apply_pending_nav, init_state
from dtsec_explorer.presentation.theme import load_css


@st.cache_data(show_spinner=False)
def cached_bundle() -> dict:
    return load_all()


def main() -> None:
    st.set_page_config(
        page_title="DTSec-Explorer",
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon="🔒",
    )
    st.markdown(load_css(), unsafe_allow_html=True)

    bundle = cached_bundle()
    init_state(bundle)

    st.markdown("# 🔒 DTSec-Explorer")
    st.markdown("### Interactive Digital Twin Security Learning Platform")
    st.caption(
        "Based on: Mun et al., “A Comprehensive Survey on Digital Twin Focusing on Security Threats and Requirements,” "
        "IEEE Access, 2025."
    )

    apply_pending_nav()
    st.sidebar.markdown("---")
    nav = st.sidebar.radio("Navigate", ["Explore", "Technologies", "Cheat sheet"], key=KEY_NAV)

    routes = {
        "Explore": render_explore,
        "Technologies": render_technologies,
        "Cheat sheet": render_cheat_sheet,
    }
    routes[nav](bundle)


if __name__ == "__main__":
    main()
