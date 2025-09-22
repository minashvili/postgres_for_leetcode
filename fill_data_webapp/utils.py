import logging

import psycopg2
import random
from typing import List
from faker import Faker

from config import Settings
from models import Field


logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


def get_db_conn(settings: Settings):

    logger.info("Connecting to DB")

    try:
        connection = psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
        )
    except Exception as e:
        logger.error(f"Error connecting to DB: {e}")
        raise e

    logger.info("Connected to DB successfully")

    return connection


def generate_value(field_type: str, fake: Faker):
    match field_type:
        case "string":
            return fake.word()
        case "int":
            return random.randint(0, 1000)
        case "email":
            return fake.email()
        case "date":
            return fake.date()
        case "float":
            return random.random()
        case _:
            return fake.word()


def create_table_if_not_exists(table: str, columns_def: str, conn, cur):
    logger.info(f"Creating table {table} if not exists")

    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table} (
            id SERIAL PRIMARY KEY,
            {columns_def}
        )
        """

    cur.execute(create_table_sql)
    conn.commit()

    logger.info(f"Table {table} is created or already exists")


def get_row_count(table, cur):
    logger.info(f"Getting row count for table {table}")
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    total_count = cur.fetchone()[0]

    logger.info(f"Total rows in table {table}: {total_count}")

    return total_count


def get_columns_definition(fields: List[Field]):
    logger.info("Generating columns definition")

    columns_sql = []
    for f in fields:
        if f.type == "int":
            col_type = "INTEGER"
        elif f.type == "date":
            col_type = "DATE"
        else:
            col_type = "TEXT"
        columns_sql.append(f"{f.name} {col_type}")
    columns_def = ", ".join(columns_sql)

    logger.info(f"Columns definition: {columns_def}")

    return columns_def


def get_insert_query(fields: List[Field], table: str):
    logger.info("Generating insert query")

    col_names = [f.name for f in fields]
    col_placeholders = ", ".join(["%s"] * len(fields))
    insert_sql = f"""
        INSERT INTO {table} ({", ".join(col_names)})
        VALUES ({col_placeholders})
        """

    logger.info(f"Insert SQL: {insert_sql}")

    return insert_sql


def insert_generated_values(row_number: int, fields, insert_sql, cur, conn):
    logger.info("Generating and inserting values")

    fake = Faker()

    generated = []
    for _ in range(row_number):
        values = [generate_value(f.type, fake) for f in fields]
        cur.execute(insert_sql, values)
        generated.append(values)

    conn.commit()

    logger.info(f"Inserted {len(generated)} rows")

    return generated
