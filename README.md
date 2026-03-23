# DTSec-Explorer

Interactive **Digital Twin Security Learning Platform** (Streamlit) built from `attacks.json`, `technologies.json`, `properties.json`, and an SFR glossary — aligned with survey (interactive security education).

## Run locally

```bash
cd "/path/to/Digital Twin"
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
streamlit run dtsec_explorer/app.py
```

Open http://localhost:8501 — optional deep link: `?attack=AT2.14`

## Run with Docker

```bash
docker compose up --build
```

`docker-compose.yml` bind-mounts `./dtsec_explorer` into the container and sets `PYTHONPATH=/app`, so imports resolve to your mounted source code (not stale installed package code). Edits to Python files apply on the next Streamlit rerun (no rebuild needed). Rebuild only when dependencies in `pyproject.toml` change.

## Data files

Place JSON under `document_references/`:

- `attacks.json` — layers and attacks (required)
- `technologies.json` — ET 1–8 definitions; `attacks_defended` is filled automatically at load time from each attack’s `enabling_tech`
- `properties.json` — six security properties; related SFRs are enriched from attacks
- `sfr_glossary.json` — short Common Criteria–style tooltips for SFR codes

## Layout

- **Explore** — layer cards, filters, attack list + detail, Plotly charts, optional compare and Sankey cascades
- **Technologies** — ET reference with links back to attacks
- **Cheat sheet** — tables by layer
- **Quiz** — random checks on layer, properties, or defenses
