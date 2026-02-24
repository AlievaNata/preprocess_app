FROM python:3.12-slim AS base

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники
COPY src ./src
COPY tests ./tests

# Открываем порт для FastAPI
EXPOSE 8000

# ---------- СБОРКА + ТЕСТЫ (аналог RUN dotnet test) ----------

FROM base AS test

WORKDIR /app

# Запуск unit-тестов при сборке образа
RUN pytest -q

# ---------- ФИНАЛЬНЫЙ ОБРАЗ ДЛЯ ЗАПУСКА ----------

FROM base AS final

WORKDIR /app

COPY --from=base /app /app

# Запуск FastAPI через uvicorn
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
