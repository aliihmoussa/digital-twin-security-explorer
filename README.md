# DTSec-Explorer

DTSec-Explorer is an interactive Streamlit application for Digital Twin security education and onboarding.  
It visualizes attacks across the three DT layers, maps security properties and Common Criteria SFRs, and links enabling technologies to defended attacks.

## What this project provides

- Layer-based exploration of Digital Twin attacks (Physical, Intermediate, Digital)
- Filterable attack catalog (property, severity, search)
- Detailed attack view (description, properties, SFRs, enabling tech, cascade effects)
- Technology reference page (ET 1-8 + defended attacks)
- Cheat sheet and quick quiz for education use
- Cross-layer summary charts for faster interpretation

## Current architecture (modular)

The codebase is split into domain logic and presentation logic:

```text
dtsec_explorer/
  app.py
  domain/
    __init__.py
    constants.py
    loaders.py
    transforms.py
    cascade.py
  presentation/
    __init__.py
    state.py
    html.py
    charts.py
    theme.py
    theme/
      styles.css
    pages/
      __init__.py
      explore.py
      technologies.py
      cheat_sheet.py
      quiz.py
```

- `domain/`: framework-agnostic business/data logic (no Streamlit UI code)
- `presentation/`: Streamlit pages, state wiring, visual components, and charts
- `app.py`: thin entrypoint/router

## Data model

Data files live in `document_references/`:

- `attacks.json` (required): layers + attack entries
- `technologies.json`: enabling technologies
- `properties.json`: security properties
- `sfr_glossary.json`: short SFR definitions used in UI tooltips

At load time:
- `attacks_defended` is derived from each attack's `enabling_tech`
- Property-level SFR sets are enriched from attack mappings

## Run locally

```bash
cd "/home/alimoussa/Documents/M2- 2026/Projects2026/Digital Twin"
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
streamlit run dtsec_explorer/app.py
```

Open: [http://localhost:8501](http://localhost:8501)  
Optional deep link example: `?attack=AT2.14`

## Run with Docker

```bash
docker compose up --build
```

Notes:
- `docker-compose.yml` bind-mounts `./dtsec_explorer` and `./document_references`
- `PYTHONPATH=/app` is set so imports resolve to mounted source code
- Rebuild when dependencies change; code-only edits reload directly

## Testing

Domain tests are under `tests/`.

```bash
python3 -m pytest -q tests
```

If `pytest` is not installed in your environment, install it first:

```bash
pip install pytest
```

## Git hygiene

The repository ignores local/runtime artifacts and large reference binaries:

- virtual env/cache files
- `*.egg-info/`
- `*.pdf` and `document_references/*.pdf`

This keeps the repo focused on source code and structured JSON data only.
