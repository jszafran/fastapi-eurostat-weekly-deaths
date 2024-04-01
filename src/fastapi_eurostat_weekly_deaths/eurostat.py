import pathlib
from typing import Iterator, Protocol, Self

import httpx

DATA_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_r_mwk_05?format=TSV&compressed=false"


class EurostatDataSource(Protocol):
    """Protocol defining methods for Eurostat Data Source."""

    def iter_lines(self) -> Iterator[str]:
        ...


class FileEurostatData:
    """
    Provides Eurostat Weekly deaths data from file (as lines of text).
    """

    def __init__(self, path: str | pathlib.Path) -> None:
        self._path = path

    def iter_lines(self) -> Iterator[str]:
        with open(self._path, "rt") as f:
            return f


class HttpEurostatData:
    """
    Provides Eurostat Weekly deaths data from Eurostat API (as lines of text).
    """

    def __init__(self, url: str = DATA_URL) -> None:
        self._url = url

    def iter_lines(self) -> Iterator[str]:
        response = httpx.get(self._url)
        response.raise_for_status()
        return response.iter_lines()


class EurostatDB:
    def __init__(self) -> None:
        self._data: dict[str, dict[str, float]] | None = None

    @staticmethod
    def _parse_header(header: str) -> list[str]:
        """Parses header string, apply data cleansing and returns it as a list of strings."""
        metadata, *time_periods = header.split("\t")
        metadata = metadata.replace(r"\TIME_PERIOD", "").split(",")
        time_periods = [x.strip() for x in time_periods]
        return metadata + time_periods

    @classmethod
    def from_data_source(cls, data_source: EurostatDataSource) -> Self:
        _ = data_source.iter_lines()
        return cls()
