import datetime
import pathlib
from collections import defaultdict
from typing import Iterator, Protocol, Self

import httpx

from fastapi_eurostat_weekly_deaths.models import DataPoint, MetadataInfo, WeekOfYear

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
    def _parse_metadata_info(metadata: str) -> MetadataInfo:
        _, age, sex, _, country = metadata.split(",")
        return MetadataInfo(
            age=age,
            sex=sex,
            country=country,
        )

    @staticmethod
    def _extract_weekly_deaths(v: str) -> int | None:
        v = v.replace("p", "").replace(":", "").strip()
        try:
            return int(v)
        except ValueError:
            return None

    @classmethod
    def from_data_source(cls, data_source: EurostatDataSource) -> Self:
        """Constructs EurostatDB from given data source (file or live Eurostat data)."""
        iterator = data_source.iter_lines()
        header = cls._parse_header(next(iterator))
        week_of_years_ix_map = {i: WeekOfYear.from_string(v) for i, v in enumerate(header[5:])}
        data = defaultdict(list)

        for line in iterator:
            metadata_str, *data_points = line.split("\t")
            metadata_info = cls._parse_metadata_info(metadata_str)
            for i, dp in enumerate(data_points):
                week_of_year = week_of_years_ix_map[i]
                data_point = DataPoint(
                    week_of_year=week_of_year,
                    metadata_info=metadata_info,
                    weekly_deaths=cls._extract_weekly_deaths(dp),
                )
                data_point_key = _data_point_db_key(data_point)
                data[data_point_key].append(data_point.weekly_deaths)

        return cls(data=data)
