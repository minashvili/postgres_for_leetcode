import psycopg2
import random
from typing import List
from faker import Faker

from config import Settings
from models import Field


def get_db_conn(settings: Settings):
    return psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )


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
    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table} (
            id SERIAL PRIMARY KEY,
            {columns_def}
        )
        """

    cur.execute(create_table_sql)
    conn.commit()


def get_row_count(table, cur):
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    total_count = cur.fetchone()[0]
    return total_count


def get_columns_definition(fields: List[Field]):
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
    return columns_def


def get_insert_query(fields: List[Field], table: str):
    col_names = [f.name for f in fields]
    col_placeholders = ", ".join(["%s"] * len(fields))
    insert_sql = f"""
        INSERT INTO {table} ({", ".join(col_names)})
        VALUES ({col_placeholders})
        """
    return insert_sql


def insert_generated_values(row_number: int, fake, fields, insert_sql, cur, conn):
    generated = []
    for _ in range(row_number):
        values = [generate_value(f.type, fake) for f in fields]
        cur.execute(insert_sql, values)
        generated.append(values)

    conn.commit()
    return generated
