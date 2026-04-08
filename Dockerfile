# Build Stage
FROM python:3.13-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev --compile-bytecode --no-install-project

COPY src/ src/

FROM python:3.13-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r screenflix && useradd -r -g screenflix -d /app screenflix

WORKDIR /app

COPY --from=builder /app/.venv .venv/
COPY --from=builder /app/src src/
COPY schemas.json .

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

USER screenflix

HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/healthz || exit 1

EXPOSE 8000

CMD ["uvicorn", "screenflix.main:app", "--host", "0.0.0.0", "--port", "8000"]