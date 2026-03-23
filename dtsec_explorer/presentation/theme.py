from __future__ import annotations

from pathlib import Path


def load_css() -> str:
    css_path = Path(__file__).resolve().parent / "theme" / "styles.css"
    content = css_path.read_text(encoding="utf-8")
    return f"<style>\n{content}\n</style>"
