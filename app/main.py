import logging

import sqlalchemy
from fastapi import FastAPI, HTTPException, Body
import uvicorn
from sqlalchemy import MetaData
from sqlalchemy.orm import Session

from app import (  # type: ignore
    models,
    utils,
    data_structure_utils,
    data_content_utils,
)
from app.config import settings


app = FastAPI()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

engine = utils.get_db_engine(settings)
db_metadata = MetaData()
db_metadata.reflect(engine)


@app.post("/create_table")
def create_table(payload: models.CreateTablePayload):
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
    data_structure_utils.create_table(
        payload.table_name, sqlalchemy_columns, engine, db_metadata
    )

    return {
        "message": "Table created successfully",
    }


@app.post("/generate")
def generate_data(payload: list[models.GeneratePayload]):
    result = {}

    db_metadata.clear()
    db_metadata.reflect(engine)

    for item in payload:
        table_name = item.table_name.lower().strip()
        table = data_structure_utils.get_existing_table(table_name, db_metadata)

        if table is None:
            raise HTTPException(404, "Table {} not found".format(table_name))

        with Session(engine) as session:
            data_content_utils.insert_generated_values(
                table, item.row_number, session, settings
            )
        total_count = data_content_utils.get_row_count(table, engine)

        result[item.table_name] = total_count

    return {
        "Total rows in tables": result,
    }


@app.post("/create_tables_leetcode")
def create_tables_leetcode(sql: str = Body(..., media_type="text/plain")):
    table_list = []
    try:
        with engine.connect() as connection:
            try:
                for statement in sql.split("\n"):
                    if not any(
                        keyword in statement.upper()
                        for keyword in ["CREATE TABLE", "TRUNCATE TABLE", "INSERT INTO"]
                    ):
                        continue
                    if statement.upper().startswith("CREATE TABLE IF NOT EXISTS"):
                        table_name = statement.split()[5]
                        table_list.append(table_name)
                    elif statement.upper().startswith("CREATE TABLE"):
                        table_name = statement.split()[2]
                        table_list.append(table_name)
                    connection.execute(sqlalchemy.text(statement))
                connection.commit()
            except Exception as e:
                connection.rollback()
                logger.error("Error executing SQL statements: {}".format(e))
                raise HTTPException(500, "Error executing SQL statements: {}".format(e))
        db_metadata.clear()
        db_metadata.reflect(engine)
    except Exception as e:
        logger.error("Database connection error: {}".format(e))
        raise HTTPException(500, "Database connection error: {}".format(e))

    return {
        "message": "LeetCode tables created successfully",
        "tables": table_list,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
