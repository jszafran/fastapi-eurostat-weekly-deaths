import pathlib

from fastapi_eurostat_weekly_deaths.eurostat import EurostatDB, FileEurostatData


def main():
    test_file = pathlib.Path(__file__).parent.parent.parent / "test_data" / "20240401.tsv"
    data_source = FileEurostatData(test_file)
    db = EurostatDB.from_data_source(data_source)
    print(db.data)


if __name__ == "__main__":
    main()
