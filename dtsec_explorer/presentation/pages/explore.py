from __future__ import annotations

from typing import Any

import streamlit as st

from dtsec_explorer.domain import LAYER_KEYS, filter_attacks
from dtsec_explorer.presentation.charts import fig_cascade_matrix, fig_layer_pie, fig_severity_bar_for_layer
from dtsec_explorer.presentation.html import prop_tag_html, severity_badge_html, sfr_html
from dtsec_explorer.presentation.state import KEY_PENDING_PROP, apply_pending_property
from dtsec_explorer.domain.cascade import cascade_layer_badges


def _layer_card_column(bundle: dict[str, Any], lk: str, layer: dict[str, Any], n: int) -> None:
    desc = layer["description"]
    if len(desc) > 130:
        desc = desc[:130].rsplit(" ", 1)[0] + "…"
    layer_idx = lk[-1] if lk and lk[-1].isdigit() else "?"
    st.markdown(
        f'<article class="layer-card" role="region" aria-label="{layer["name"]}">'
        f'<p class="layer-card-eyebrow">Layer {layer_idx}</p>'
        f'<h4 class="layer-card-title">{layer["name"]}</h4>'
        f'<p class="layer-card-desc">{desc}</p>'
        f'<p class="layer-card-meta"><span class="layer-count">{n}</span> attacks</p>'
        f"</article>",
        unsafe_allow_html=True,
    )
    label = f"Open {layer['name'].split()[0]} layer"
    if st.button(label, key=f"pick_{lk}", use_container_width=True):
        st.session_state.layer_key = lk
        st.session_state.attack_id = bundle["attacks_root"][lk]["attacks"][0]["id"]
        st.query_params.pop("attack", None)
        st.rerun()


def render_layer_cards(bundle: dict[str, Any]) -> None:
    st.markdown("### Select a layer")
    cols = st.columns(3, gap="medium")
    for i, lk in enumerate(LAYER_KEYS):
        layer = bundle["attacks_root"][lk]
        with cols[i]:
            _layer_card_column(bundle, lk, layer, len(layer["attacks"]))


def render_attack_detail(attack: dict[str, Any], bundle: dict[str, Any]) -> None:
    glossary = bundle["sfr_glossary"]
    pmap = bundle["property_by_name"]

    st.markdown(f"## {attack['id']} — {attack['name']} {severity_badge_html(attack['severity'])}", unsafe_allow_html=True)
    st.caption(f"{attack['layer_name']} · {attack['layer_key']}")

    t1, t2, t3, t4 = st.tabs(["Overview", "Properties & SFRs", "Defenses & tech", "Cascade effects"])
    with t1:
        st.markdown(attack["description"])
    with t2:
        row = " ".join(prop_tag_html(p, pmap.get(p, {}).get("color", "#999")) for p in attack.get("security_properties", []))
        st.markdown("**Security properties** (from survey taxonomy)")
        st.markdown(row, unsafe_allow_html=True)
        for prop in attack.get("security_properties", []):
            with st.expander(f"About **{prop}**"):
                st.markdown(pmap.get(prop, {}).get("description", "_No description._"))
        st.markdown("---")
        st.markdown("**Security Functional Requirements (Common Criteria)** — hover for short definitions")
        st.markdown(" ".join(sfr_html(code, glossary) for code in attack.get("sfrs", [])), unsafe_allow_html=True)
    with t3:
        techs = bundle["technologies"]
        by_id = {t["id"]: t for t in techs}
        st.markdown("**Enabling technologies** referenced for this attack (survey Idea 7)")
        for et in attack.get("enabling_tech", []):
            tech = by_id.get(et)
            if not tech:
                st.write(et)
                continue
            with st.expander(f"{tech['id']}: {tech['name']}"):
                st.markdown(tech["description"])
                st.markdown("**Provides (properties):** " + ", ".join(tech.get("security_properties", [])))
                st.markdown("**Example SFRs:** " + ", ".join(f"`{s}`" for s in tech.get("sfrs", [])))

        defenders = [t for t in techs if attack["id"] in t.get("attacks_defended", [])]
        st.markdown("---")
        st.markdown("**View defenses** — technologies that explicitly list this attack as defended")
        if defenders:
            for tech in defenders:
                st.success(f"{tech['id']} **{tech['name']}** covers this attack among others.")
        else:
            st.info("Use enabling technologies above; `attacks_defended` is derived from `enabling_tech` in JSON.")
    with t4:
        st.markdown("**Downstream effects** described in the survey (qualitative links, not a formal threat graph).")
        for ce in attack.get("cascade_effects", []):
            st.markdown(f"- {cascade_layer_badges(ce)}")


def render_compare(bundle: dict[str, Any], ids: list[str]) -> None:
    if len(ids) < 2:
        st.info("Select at least two attacks to compare.")
        return
    cols = st.columns(min(len(ids), 3))
    for col, aid in zip(cols, ids):
        attack = bundle["attack_by_id"].get(aid)
        if not attack:
            continue
        with col:
            st.markdown(f"### {attack['id']}")
            st.markdown(severity_badge_html(attack["severity"]), unsafe_allow_html=True)
            st.markdown(attack["name"])
            st.caption(attack["layer_name"])
            st.markdown("**Properties:** " + ", ".join(attack.get("security_properties", [])))
            st.markdown("**SFRs:** " + ", ".join(f"`{s}`" for s in attack.get("sfrs", [])))
            st.markdown("**Tech:** " + ", ".join(attack.get("enabling_tech", [])))


def render(bundle: dict[str, Any]) -> None:
    apply_pending_property()
    render_layer_cards(bundle)
    lk = st.session_state.layer_key
    layer = bundle["attacks_root"][lk]

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    props_list = ["All"] + [p["name"] for p in bundle["properties"]]
    prop_sel = st.sidebar.selectbox("Security property", props_list, key="f_prop")
    if st.sidebar.button("Clear property filter"):
        st.session_state[KEY_PENDING_PROP] = "All"
        st.rerun()

    sev_opts = ["Critical", "High", "Medium", "Low"]
    sev_sel = st.sidebar.multiselect("Severity", sev_opts, default=sev_opts, key="f_sev")
    search = st.sidebar.text_input("Search id / name / description", key="f_search")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Quick property filter")
    for p in bundle["properties"]:
        label = f"● {p['name']}"
        if st.sidebar.button(label, key=f"propbtn_{p['name']}", help=p["description"][:200]):
            st.session_state[KEY_PENDING_PROP] = p["name"]
            st.rerun()

    filtered = filter_attacks(bundle["flat_attacks"], lk, prop_sel, sev_sel, search)
    st.caption(f"Showing **{len(filtered)}** attacks (layer total {len(layer['attacks'])} · dataset total 53)")

    c_list, c_detail = st.columns([1, 1.35])
    with c_list:
        st.subheader("Attack list")
        if not filtered:
            st.warning("No attacks match filters.")
            return
        labels = [f"{a['id']} — {a['name']}" for a in filtered]
        ids = [a["id"] for a in filtered]
        default_i = ids.index(st.session_state.attack_id) if st.session_state.attack_id in ids else 0
        pick = st.selectbox("Select attack", range(len(labels)), format_func=lambda i: labels[i], index=default_i, label_visibility="collapsed")
        st.session_state.attack_id = ids[pick]
        st.query_params["attack"] = st.session_state.attack_id

        preview = filtered[pick]
        st.markdown(f"{severity_badge_html(preview['severity'])} {preview['id']}", unsafe_allow_html=True)
        st.markdown(f"**{preview['name']}**")
        st.write(preview["description"][:280] + ("…" if len(preview["description"]) > 280 else ""))
        pmap = bundle["property_by_name"]
        tags = " ".join(prop_tag_html(x, pmap.get(x, {}).get("color", "#999")) for x in preview.get("security_properties", []))
        st.markdown(tags, unsafe_allow_html=True)

    with c_detail:
        st.subheader("Attack detail")
        render_attack_detail(bundle["attack_by_id"][st.session_state.attack_id], bundle)

    st.markdown("---")
    st.subheader("Visualizations")
    ec1, ec2 = st.columns(2)
    with ec1:
        st.plotly_chart(fig_layer_pie(bundle["flat_attacks"]), use_container_width=True)
    with ec2:
        st.plotly_chart(fig_severity_bar_for_layer(bundle["flat_attacks"], lk), use_container_width=True)
    with st.expander("Cross-layer cascade summary", expanded=False):
        st.caption(
            "**How to read this:** rows are source layers (where attacks originate), columns are impacted layers "
            "mentioned in `cascade_effects`. Each cell is the number of attacks that mention this source -> target impact."
        )
        st.plotly_chart(fig_cascade_matrix(bundle["flat_attacks"]), use_container_width=True)

    with st.expander("Compare attacks (side by side)", expanded=False):
        opts = [f"{a['id']} — {a['name']}" for a in bundle["flat_attacks"]]
        comp = st.multiselect("Pick 2–3 attacks", options=opts, max_selections=3, key="compare_pick")
        id_map = {f"{a['id']} — {a['name']}": a["id"] for a in bundle["flat_attacks"]}
        render_compare(bundle, [id_map[x] for x in comp])
