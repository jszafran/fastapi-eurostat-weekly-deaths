FROM python:3.12

WORKDIR /app

COPY pyproject.toml /app/

RUN mkdir -p /app/src/fastapi_eurostat_weekly_deaths
RUN touch /app/src/fastapi_eurostat_weekly_deaths/__init__.py

RUN pip install -e . --no-cache-dir

COPY src /app/src
