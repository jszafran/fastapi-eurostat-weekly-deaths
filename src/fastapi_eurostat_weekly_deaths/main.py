import pathlib

import uvicorn
from fastapi import FastAPI

from fastapi_eurostat_weekly_deaths.eurostat import EurostatDB, FileEurostatData

app = FastAPI()


@app.get("/")
async def index():
    return {"Hello": "world"}


@app.on_event("startup")
def eurostat_database() -> None:
    print("Starting database")
    test_file = pathlib.Path(__file__).parent.parent.parent / "test_data" / "20240401.tsv"
    data_source = FileEurostatData(test_file)
    db = EurostatDB.from_data_source(data_source)
    app.eurostat_db = db


if __name__ == "__main__":
    uvicorn.run(app, port=8888)
