FROM python:3.12-slim-bookworm as builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Установка Poetry
ENV POETRY_VERSION=2.1.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry --version

# Копирование зависимостей
COPY pyproject.toml poetry.lock ./

# Установка зависимостей без dev-пакетов
RUN poetry install --only=main --no-root --no-interaction --no-ansi

# Финальный образ
FROM python:3.12-slim-bookworm as runtime

WORKDIR /app

# Копирование виртуального окружения из builder
COPY --from=builder /app/.venv ./.venv
ENV PATH="/app/.venv/bin:$PATH"

# Создание непривилегированного пользователя
#RUN groupadd -r appuser && \
#    useradd -r -g appuser appuser && \
#    chown -R appuser:appuser /app
#USER appuser

# Копирование исходного кода
COPY --chown=appuser:appuser ./app ./app

# Оптимизация переменных окружения Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1
