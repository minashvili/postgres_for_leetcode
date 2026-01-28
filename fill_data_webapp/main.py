import logging

from fastapi import FastAPI, HTTPException
import uvicorn
from sqlalchemy import MetaData
from sqlalchemy.orm import Session

from fill_data_webapp import (
    models,
    utils,
    data_structure_utils,
    data_content_utils,
)
from fill_data_webapp.config import settings


app = FastAPI()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

engine = utils.get_db_engine(settings)
db_metadata = MetaData()
db_metadata.reflect(engine)


@app.post("/generate")
def generate_data(payload: models.Payload):
    existing_table = data_structure_utils.get_existing_table(
        payload.table_name, db_metadata
    )

    if existing_table is not None:
        if payload.force_recreate_table:
            data_structure_utils.drop_table(existing_table, db_metadata, engine)
        else:
            raise HTTPException(
                500,
                "Table already exists. Use force_recreate_table to drop and recreate.",
            )

    sqlalchemy_columns = data_structure_utils.get_columns_definition(
        payload.fields, settings
    )
    table = data_structure_utils.create_table(
        payload.table_name, sqlalchemy_columns, engine, db_metadata
    )
    with Session(engine) as session:
        data_content_utils.insert_generated_values(
            table, payload.row_number, payload.fields, session, settings
        )
    total_count = data_content_utils.get_row_count(table, engine)

    return {
        "inserted_rows": total_count,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
