"""
Module containing functions responsible for parsing Eurostat data.
"""
from fastapi_eurostat_weekly_deaths.models import MetadataInfo, WeekOfYear


def parse_header(header: str) -> list[str]:
    """Parses header string, applies data cleansing and returns it as a list of strings."""
    metadata_str, *time_periods = header.strip().split("\t")
    metadata = metadata_str.replace(r"\TIME_PERIOD", "").split(",")
    time_periods = [x.strip() for x in time_periods]
    return metadata + time_periods


def is_header_sorted(header: list[str]) -> bool:
    weeks_of_year = [WeekOfYear.from_string(col) for col in header]
    return weeks_of_year == sorted(weeks_of_year, key=lambda x: (x.year, x.week))


def parse_metadata_info(metadata: str) -> MetadataInfo:
    _, age, sex, _, country = metadata.split(",")
    return MetadataInfo(
        age=age,
        sex=sex,
        country=country,
    )


def extract_weekly_deaths(v: str) -> int | None:
    v = v.replace("p", "").replace(":", "").strip()
    try:
        return int(v)
    except ValueError:
        return None
