FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    DTSEC_DATA_DIR=/app/document_references

COPY pyproject.toml README.md ./
COPY dtsec_explorer ./dtsec_explorer
COPY document_references ./document_references

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

EXPOSE 8501

CMD ["streamlit", "run", "dtsec_explorer/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
