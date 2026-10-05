FROM python:3.12-slim@sha256:2f17fc044b579bab302c2e8054d3a686e2cb9a83de48e70534b94cd8ebbe06a9

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_PATH=/app/models/modelo.json

WORKDIR /app
COPY requirements-backend.txt ./
RUN pip install --no-cache-dir --only-binary=:all: -r requirements-backend.txt \
    && groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home app
ENV MPLCONFIGDIR=/tmp/matplotlib
COPY backend/app.py ./backend/app.py

USER app
EXPOSE 6767
CMD ["python", "backend/app.py", "--host", "0.0.0.0", "--port", "6767"]
