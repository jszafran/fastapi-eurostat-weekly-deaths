from typing import List, Self

from pydantic import BaseModel


class MetadataInfo(BaseModel):
    age: str
    sex: str
    country: str


class WeekOfYear(BaseModel):
    week: int
    year: int

    @classmethod
    def from_string(cls, v: str) -> Self:
        year_str, week_str = v.split("-")
        year = int(year_str)
        week = int(week_str.replace("W", ""))
        return cls(week=week, year=year)


class DataPoint(BaseModel):
    week_of_year: WeekOfYear
    metadata_info: MetadataInfo
    weekly_deaths: int | None = None


class WeeklyDeathsQuery(BaseModel):
    countries: List[str]
    year_from: int
    year_to: int
    age: str | None = "TOTAL"
    sex: str | None = "T"


class CountryYearlyData(BaseModel):
    year: int
    country: str
    weekly_deaths: List[int | None]
