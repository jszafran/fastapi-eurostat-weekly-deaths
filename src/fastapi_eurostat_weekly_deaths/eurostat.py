import datetime
import pathlib
from typing import Iterator, Protocol, Self

import httpx

from fastapi_eurostat_weekly_deaths.models import MetadataInfo, WeekOfYear

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


class EurostatDB:
    """In-memory database serving Eurostat Weekly Deaths data."""

    def __init__(self) -> None:
        self._data: dict[str, dict[str, float]] | None = None
        self.snapshot_date: datetime.date | None = None

    @staticmethod
    def _parse_header(header: str) -> list[str]:
        """Parses header string, apply data cleansing and returns it as a list of strings."""
        metadata_str, *time_periods = header.strip().split("\t")
        metadata = metadata_str.replace(r"\TIME_PERIOD", "").split(",")
        time_periods = [x.strip() for x in time_periods]
        return metadata + time_periods

    @staticmethod
    def _is_header_sorted(header: list[str]) -> bool:
        weeks_of_year = [WeekOfYear.from_string(col) for col in header]
        return weeks_of_year == sorted(weeks_of_year, key=lambda x: (x.year, x.week))

    @staticmethod
    def parse_metadata_info(metadata: str) -> MetadataInfo:
        _, age, sex, _, country = metadata.split(",")
        return MetadataInfo(
            age=age,
            sex=sex,
            country=country,
        )

    def extract_weekly_deaths(self, v: str) -> float | None:
        pass

    @classmethod
    def from_data_source(cls, data_source: EurostatDataSource) -> Self:
        """Constructs EurostatDB from given data source (file or live Eurostat data)."""
        iterator = data_source.iter_lines()
        header = cls._parse_header(next(iterator))
        print(cls._is_header_sorted(header[5:]))
        for line in iterator:
            metadata, *data_points = line.split("\t")
            _, age, sex, _, country = metadata.split(",")

        return cls()
