import logging

import psycopg2
import random
from typing import List
from faker import Faker

from config import Settings
from models import Field, FieldType

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


def generate_single_value(field_type: FieldType, fake: Faker):
    match field_type:
        case FieldType.int:
            return random.randint(1, 1_000_000_000)
        case FieldType.email:
            return fake.email()
        case FieldType.date:
            return fake.date()
        case FieldType.float:
            return round(random.uniform(1, 1_000_000_000), 2)
        case FieldType.multistring:
            word_count = random.randint(2, 30)
            return " ".join(fake.words(nb=word_count))

    return fake.word()


def generate_values(fields: List[Field], fake: Faker, row_number: int):
    if len(fields) == 0:
        raise ValueError("No fields provided for value generation")

    unique_values = {
        f.name: set()
        for f in fields
        if "unique" in f.constraints or "primary" in f.constraints
    }
    rows = []

    for _ in range(row_number):
        row = []
        for field in fields:
            value = generate_single_value(field.type, fake)

            if "not null" in field.constraints or "primary" in field.constraints:
                while value is None:
                    value = generate_single_value(field.type, fake)

            if "unique" in field.constraints or "primary" in field.constraints:
                while value in unique_values[field.name]:
                    value = generate_single_value(field.type, fake)
                unique_values[field.name].add(value)

            row.append(value)
        rows.append(row)
    return rows


def create_table_if_not_exists(table: str, columns_def: str, conn, cur):
    logger.info(f"Creating table {table} if not exists")

    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table} (
            {columns_def}
        )
        """

    cur.execute(create_table_sql)
    conn.commit()

    logger.info(f"Table {table} is created or already exists")


def get_row_count(table, cur):
    logger.info(f"Getting row count for table {table}")
    try:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        total_count = cur.fetchone()[0]

        logger.info(f"Total rows in table {table}: {total_count}")

        return total_count
    except Exception as e:
        logger.error(f"Error getting row count for table {table}: {e}")
        raise e


def get_columns_definition(fields: List[Field]) -> str:
    logger.info("Generating columns definition")

    if len(fields) == 0:
        raise ValueError("No fields provided for columns definition generation")

    columns_sql = []
    primary_keys = []

    for f in fields:
        match f.type:
            case FieldType.int:
                col_type = "INTEGER"
            case FieldType.date:
                col_type = "DATE"
            case FieldType.float:
                col_type = "REAL"
            case _:
                col_type = "TEXT"

        constraints = []
        for constraint in f.constraints:
            match constraint:
                case "not null":
                    constraints.append("NOT NULL")
                case "unique":
                    constraints.append("UNIQUE")
                case "primary":
                    primary_keys.append(f.name)
                    constraints.append("NOT NULL")

        col_def = f"{f.name} {col_type} {' '.join(constraints)}"
        columns_sql.append(col_def)

    columns_def = ", ".join(columns_sql)
    columns_def += f", PRIMARY KEY ({', '.join(primary_keys)})" if primary_keys else ""

    logger.info(f"Columns definition: {columns_def}")

    return columns_def


def get_insert_query(fields: List[Field], table: str):
    logger.info("Generating insert query")

    if len(fields) == 0:
        raise ValueError("No fields provided for insert query generation")

    col_names = [f.name for f in fields]
    col_placeholders = ", ".join(["%s"] * len(fields))
    insert_sql = (
        f"INSERT INTO {table} ({', '.join(col_names)}) VALUES ({col_placeholders})"
    )

    logger.info(f"Insert SQL: {insert_sql}")

    return insert_sql


def insert_generated_values(row_number: int, fields, insert_sql, cur, conn) -> List:
    logger.info("Generating and inserting values")

    fake = Faker()

    values = generate_values(fields, fake, row_number)

    try:
        for row in values:
            cur.execute(insert_sql, row)

        conn.commit()

        logger.info(f"Inserted {len(values)} rows")
    except Exception as e:
        logger.error(f"Error inserting row {row}: {e}")
        raise e

    return values
