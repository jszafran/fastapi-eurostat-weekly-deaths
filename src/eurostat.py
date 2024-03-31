import gzip

DATA_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_r_mwk_05?format=TSV&compressed=true"


def parse_header(header: str) -> list[str]:
    """
    Parses header string, apply data cleansing and returns it as a list of strings.
    """
    metadata, *time_periods = header.split("\t")
    metadata = metadata.replace("\TIME_PERIOD", "").split(",")
    time_periods = [x.strip() for x in time_periods]
    return metadata + time_periods


def parse_eurostat_data():
    with gzip.open("test_data/test_input.tsv.gz", "rt") as f:
        print(parse_header(next(f).strip()))



if __name__ == '__main__':
    parse_eurostat_data()
