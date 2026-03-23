from __future__ import annotations


def severity_badge_html(severity: str) -> str:
    cls = {
        "Critical": "sev-critical",
        "High": "sev-high",
        "Medium": "sev-medium",
        "Low": "sev-low",
    }.get(severity, "sev-medium")
    return f'<span class="{cls}">{severity}</span>'


def prop_tag_html(name: str, color: str) -> str:
    return f'<span class="prop-tag" style="background:{color}55;border:1px solid {color};color:#fff;">{name}</span>'


def sfr_html(code: str, glossary: dict[str, str]) -> str:
    tip = glossary.get(code, "Common Criteria security functional requirement")
    safe_tip = tip.replace('"', "&quot;")
    return (
        f'<abbr title="{safe_tip}" style="text-decoration:none;border-bottom:1px dotted #666;">'
        f'<span class="sfr-code">{code}</span></abbr>'
    )
