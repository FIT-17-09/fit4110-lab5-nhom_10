# syntax=docker/dockerfile:1.7

FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

RUN python -m venv /opt/venv

COPY requirements.txt .

# Install CPU version of ultralytics for mock/lightweight usage
RUN /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

ENV SERVICE_NAME=ai-vision
ENV SERVICE_VERSION=1.0.0
ENV AUTH_TOKEN=a4-dev-token
ENV USE_MOCK_AI=true

WORKDIR /app

RUN addgroup --system aigroup \
    && adduser --system --ingroup aigroup --home /app aiuser

COPY --from=builder /opt/venv /opt/venv
COPY src/ ./src/

RUN chown -R aiuser:aigroup /app

USER aiuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()" || exit 1

CMD ["sh", "-c", "uvicorn ai_vision.main:app --app-dir src --host 0.0.0.0 --port 8000"]
