from __future__ import annotations

import random
from typing import Any

import streamlit as st

from dtsec_explorer.domain import LAYER_KEYS


def render(bundle: dict[str, Any]) -> None:
    st.subheader("Quick quiz")
    flat = bundle["flat_attacks"]

    if st.button("New random question", key="quiz_new"):
        st.session_state.quiz_attack = random.choice(flat)
        st.session_state.quiz_qtype = random.choice(["layer", "props", "tech"])
        st.rerun()

    if "quiz_attack" not in st.session_state:
        st.session_state.quiz_attack = random.choice(flat)
        st.session_state.quiz_qtype = random.choice(["layer", "props", "tech"])

    attack = st.session_state.quiz_attack
    qtype = st.session_state.quiz_qtype

    st.markdown(f"**Attack:** {attack['id']} — {attack['name']}")
    st.write(attack["description"][:400] + ("…" if len(attack["description"]) > 400 else ""))

    if qtype == "layer":
        st.markdown("Which **layer** does this attack belong to?")
        opts = {bundle["attacks_root"][k]["name"]: k for k in LAYER_KEYS}
        ans = st.radio("Layer", list(opts.keys()), horizontal=True)
        if st.button("Check answer", key="chk_layer"):
            ok = opts[ans] == attack["layer_key"]
            st.success("Correct!") if ok else st.error(f"Not quite — this attack is in **{attack['layer_name']}**.")
    elif qtype == "props":
        st.markdown("Select **one security property** that applies (there may be several correct; one is enough for practice).")
        props = attack.get("security_properties", [])
        pool = [p["name"] for p in bundle["properties"] if p["name"] not in props]
        random.shuffle(pool)
        choices = props + pool[:3]
        random.shuffle(choices)
        ans = st.radio("Property", choices)
        if st.button("Check answer", key="chk_prop"):
            st.success("Correct!") if ans in props else st.error(f"Expected one of: {', '.join(props)}")
    else:
        st.markdown("Which **enabling technology** is listed for this attack?")
        correct = set(attack.get("enabling_tech", []))
        wrong = [t["id"] for t in bundle["technologies"] if t["id"] not in correct]
        random.shuffle(wrong)
        choices = list(correct) + wrong[:3]
        random.shuffle(choices)
        ans = st.radio("Technology", choices)
        if st.button("Check answer", key="chk_tech"):
            st.success("Correct!") if ans in correct else st.error(f"Listed: {', '.join(sorted(correct))}")
