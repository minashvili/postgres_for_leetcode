import logging

from typing import List

import sqlalchemy
from sqlalchemy import (
    Engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    Date,
    Boolean,
    Text,
)

from app.config import Settings
from app.models import Field

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


def get_existing_table(table_name: str, db_metadata: MetaData) -> Table | None:
    logger.info("Getting existing columns in DB for table {}".format(table_name))

    table_name = table_name.strip()

    if table_name in db_metadata.tables:
        return db_metadata.tables[table_name]

    public_table_name = f"public.{table_name}"
    if public_table_name in db_metadata.tables:
        return db_metadata.tables[public_table_name]

    return None


def get_columns_definition(fields: List[Field], settings: Settings) -> list[Column]:
    logger.info("Generating columns definition")

    if len(fields) == 0:
        raise ValueError("No fields provided for columns definition generation")

    type_mapping = {
        "integer": Integer,
        "email": String(settings.string_length),
        "string": String(settings.string_length),
        "float": Float,
        "date": Date,
        "boolean": Boolean,
        "text": Text,
    }
    sqlalchemy_columns: list[sqlalchemy.Column] = []

    for f in fields:
        col_type: object = type_mapping.get(f.type.lower())

        field_params = {"name": f.name, "type_": col_type}

        if f.primary_key:
            field_params["primary_key"] = f.primary_key
        if f.nullable:
            field_params["nullable"] = f.nullable
        if f.unique:
            field_params["unique"] = f.unique
        sqlalchemy_columns.append(Column(**field_params))  # type: ignore

    logger.info("Columns definition: {}".format(sqlalchemy_columns))

    return sqlalchemy_columns


def create_table(
    table_name: str,
    sqlalchemy_columns: list[Column],
    engine: Engine,
    metadata: MetaData,
):
    logger.info("Creating table {}".format(table_name))

    try:
        with engine.begin() as conn:
            table = Table(table_name, metadata, *sqlalchemy_columns)
            metadata.create_all(conn)

            logger.info("Table {} is created".format(table_name))
    except Exception as e:
        logger.error("Error creating table: {}".format(e))
        raise

    return table


def drop_table(table: Table, metadata: MetaData, engine: Engine):
    logger.info("Dropping table {}".format(table.name))

    try:
        with engine.begin() as conn:
            metadata.drop_all(conn, [table], checkfirst=True)
            metadata.remove(table)

            logger.info("Table {} dropped".format(table.name))
    except Exception as e:
        logger.error("Error dropping table {}: {}".format(table.name, e))
        raise e
