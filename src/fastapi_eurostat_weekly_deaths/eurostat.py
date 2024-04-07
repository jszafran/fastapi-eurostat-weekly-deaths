import datetime
import pathlib
from collections import defaultdict
from typing import Iterator, Protocol, Self

import httpx

from fastapi_eurostat_weekly_deaths import data_parser
from fastapi_eurostat_weekly_deaths.models import DataPoint, WeekOfYear

DATA_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_r_mwk_05?format=TSV&compressed=false"


class EurostatDataSource(Protocol):
    """Protocol defining methods for Eurostat Data Source."""

    def iter_lines(self) -> Iterator[str]:
        ...


class FileEurostatData:
    """Provides Eurostat Weekly deaths data from file (as lines of text)."""

    def __init__(self, path: str | pathlib.Path) -> None:
        self._path = path

    def iter_lines(self) -> Iterator[str]:
        with open(self._path, "rt") as f:
            for line in f:
                yield line


class HttpEurostatData:
    """Provides Eurostat Weekly deaths data from Eurostat API (as lines of text)."""

    def __init__(self, url: str = DATA_URL) -> None:
        self._url = url

    def iter_lines(self) -> Iterator[str]:
        response = httpx.get(self._url)
        response.raise_for_status()
        return response.iter_lines()


def _data_point_db_key(dp: DataPoint) -> str:
    country = dp.metadata_info.country
    sex = dp.metadata_info.sex
    age = dp.metadata_info.age
    year = dp.week_of_year.year
    return f"{country}-{year}-{sex}-{age}"


class EurostatDB:
    """In-memory database serving Eurostat Weekly Deaths data."""

    def __init__(self, data: dict[str, list[int | None]]) -> None:
        self.data: dict[str, list[int | None]] = data
        self.snapshot_date: datetime.date | None = None

    @classmethod
    def from_data_source(cls, data_source: EurostatDataSource) -> Self:
        """Constructs EurostatDB from given data source (file or live Eurostat data)."""

        iterator = data_source.iter_lines()
        header = data_parser.parse_header(next(iterator))
        week_of_years_ix_map = {i: WeekOfYear.from_string(v) for i, v in enumerate(header[5:])}
        data = defaultdict(list)

        for line in iterator:
            metadata_str, *data_points = line.split("\t")
            metadata_info = data_parser.parse_metadata_info(metadata_str)
            for i, dp in enumerate(data_points):
                week_of_year = week_of_years_ix_map[i]
                data_point = DataPoint(
                    week_of_year=week_of_year,
                    metadata_info=metadata_info,
                    weekly_deaths=data_parser.extract_weekly_deaths(dp),
                )
                data_point_key = _data_point_db_key(data_point)
                data[data_point_key].append(data_point.weekly_deaths)

        return cls(data=data)
