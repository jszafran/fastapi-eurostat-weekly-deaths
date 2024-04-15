import sys
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator

import loguru
from fastapi import FastAPI, Query
from starlette.responses import PlainTextResponse

from fastapi_eurostat_weekly_deaths.eurostat import EurostatDB, HttpEurostatData
from fastapi_eurostat_weekly_deaths.models import CountryYearlyData, WeeklyDeathsQuery


class EurostatAPI(FastAPI):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logger: loguru.Logger | None = None
        self.db: EurostatDB | None = None


@asynccontextmanager  # noqa
async def lifespan(app: EurostatAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    if app.logger is None:
        raise RuntimeError()
    app.logger.info("Starting the database.")
    data_source = HttpEurostatData()
    db = EurostatDB.from_data_source(data_source)
    app.db = db
    app.logger.info("Database created successfully.")
    yield


app = EurostatAPI(lifespan=lifespan)


def setup_logging():
    from loguru import logger

    # add loguru handler
    logger.add(
        sys.stderr,
        format="{time} {level} {message}",
        level="INFO",
    )

    app.logger = logger
    app.logger.info("Logger has been setup.")


@app.get("/api/healthcheck/", response_class=PlainTextResponse)
async def healthcheck():
    return "200"


@app.get("/api/weekly_deaths/")
def get_weekly_deaths(
    countries: Annotated[list[str], Query()],
    year_from: int,
    year_to: int,
    age: str | None = "TOTAL",
    sex: str | None = "T",
) -> list[CountryYearlyData]:
    query = WeeklyDeathsQuery(
        countries=countries,
        year_from=year_from,
        year_to=year_to,
        age=age,
        sex=sex,
    )
    result = app.db.query_weekly_deaths(query)  # type: ignore
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, log_config=None)
