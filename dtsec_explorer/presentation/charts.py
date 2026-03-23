"""Plotly charts for DTSec-Explorer."""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dtsec_explorer.domain import SEVERITY_COLORS, build_cascade_sankey


def fig_layer_pie(flat_attacks: list[dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(
        {
            "layer": [a["layer_name"] for a in flat_attacks],
            "color": [a["layer_color"] for a in flat_attacks],
        }
    )
    counts = df.groupby("layer", as_index=False).size()
    layer_first = df.groupby("layer", as_index=False).first()
    color_map = dict(zip(layer_first["layer"], layer_first["color"]))
    colors = [color_map.get(l, "#cccccc") for l in counts["layer"]]
    fig = px.pie(
        counts,
        values="size",
        names="layer",
        title="Attack distribution by DT layer",
        color_discrete_sequence=colors,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(margin=dict(t=40, b=20, l=20, r=20), height=380)
    return fig


def fig_severity_bar_for_layer(
    flat_attacks: list[dict[str, Any]], layer_key: str | None
) -> go.Figure:
    if layer_key:
        subset = [a for a in flat_attacks if a["layer_key"] == layer_key]
        title = f"Attacks by severity — {subset[0]['layer_name'] if subset else layer_key}"
    else:
        subset = flat_attacks
        title = "Attacks by severity (all layers)"
    if not subset:
        fig = go.Figure()
        fig.update_layout(title=title, height=320)
        return fig
    order = ["Critical", "High", "Medium", "Low"]
    df = pd.DataFrame(subset)
    counts = df["severity"].value_counts().reindex(order).fillna(0).astype(int).reset_index()
    counts.columns = ["severity", "count"]
    fig = px.bar(
        counts,
        x="severity",
        y="count",
        title=title,
        color="severity",
        color_discrete_map=SEVERITY_COLORS,
        category_orders={"severity": order},
    )
    fig.update_layout(showlegend=False, margin=dict(t=40, b=40, l=40, r=20), height=340)
    return fig


def fig_cascade_sankey(flat_attacks: list[dict[str, Any]]) -> go.Figure:
    labels, source, target, value = build_cascade_sankey(flat_attacks)
    if not value:
        fig = go.Figure()
        fig.update_layout(
            title="Cross-layer cascade flows (from cascade_effects text)",
            annotations=[dict(text="No parsed layer-to-layer links", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)],
            height=400,
        )
        return fig
    # Fixed horizontal layout (L1 → L2 → L3) reduces confusing default routing / “looping” ribbons.
    n_nodes = len(labels)
    node_colors = ["#FFE5E5", "#E5FFE5", "#E5E5FF"][:n_nodes]
    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    label=labels,
                    x=[0.02, 0.5, 0.98],
                    y=[0.5, 0.5, 0.5],
                    pad=28,
                    thickness=22,
                    color=node_colors,
                    line=dict(color="rgba(0,0,0,0.25)", width=1),
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=value,
                    color=["rgba(150,160,200,0.35)"] * len(source),
                    hovertemplate="%{value} attack(s)<extra></extra>",
                ),
            )
        ]
    )
    fig.update_layout(
        title=dict(
            text="Aggregated cascade mentions across layers (survey cascade text)",
            font=dict(size=15),
        ),
        font=dict(size=13, color="#e8eaed"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, b=30, l=24, r=24),
        height=460,
        template="plotly_dark",
    )
    return fig


def fig_cascade_matrix(flat_attacks: list[dict[str, Any]]) -> go.Figure:
    """Readable alternative to Sankey: 3x3 source->target cascade count matrix."""
    labels, source, target, value = build_cascade_sankey(flat_attacks)
    n = len(labels)
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    for s, t, v in zip(source, target, value):
        matrix[s][t] += int(v)

    fig = go.Figure(
        data=go.Heatmap(
            z=matrix,
            x=labels,
            y=labels,
            colorscale="Blues",
            text=matrix,
            texttemplate="%{text}",
            hovertemplate="From %{y}<br>To %{x}<br>Count: %{z}<extra></extra>",
            zmin=0,
        )
    )
    fig.update_layout(
        title="Cross-layer cascade matrix (source layer -> impacted layer)",
        xaxis_title="Impacted layer",
        yaxis_title="Source layer",
        margin=dict(t=50, b=40, l=40, r=20),
        height=420,
    )
    return fig
