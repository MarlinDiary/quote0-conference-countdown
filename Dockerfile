FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

COPY . .
RUN /app/.venv/bin/python -m compileall -q /app

ENV PYTHONUNBUFFERED=1 \
    UPDATE_INTERVAL=10800 \
    QUOTE_PUSH_ENABLED=false \
    CONFERENCE_CONFIG_URL=https://raw.githubusercontent.com/MarlinDiary/quote0-conference-countdown/main/conference.yml \
    PREVIEW_PATH=/tmp/conference-countdown.png

CMD ["/app/.venv/bin/python", "display.py", "--loop"]
