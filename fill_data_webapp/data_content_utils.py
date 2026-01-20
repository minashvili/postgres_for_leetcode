import logging

import random
from collections import defaultdict
from typing import List
from faker import Faker
import sqlalchemy
from sqlalchemy import (
    Engine,
    Table,
)
from sqlalchemy.orm import Session

from fill_data_webapp.models import Field, FieldType

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


def generate_single_value(field_type: FieldType, fake: Faker):
    match field_type:
        case FieldType.integer:
            return random.randint(0, 1_000_000_000)
        case FieldType.email:
            return fake.email()
        case FieldType.date:
            return fake.date()
        case FieldType.float:
            return round(random.uniform(-1_000_000_000, 1_000_000_000), 2)
        case FieldType.text:
            word_count = random.randint(0, 30)
            return " ".join(fake.words(nb=word_count))

    return fake.word()


def generate_values(fields: List[Field], fake: Faker, row_number: int):
    if len(fields) == 0:
        raise ValueError("No fields provided for value generation")

    rows = []
    unique_values: defaultdict = defaultdict(set)
    for _ in range(row_number):
        generated_values = {}
        for field in fields:
            value = generate_single_value(field.type, fake)

            if field.nullable:
                random_int = random.randint(0, 100)
                if random_int == 0:
                    value = None

            if field.unique:
                while value in unique_values[field.name]:
                    value = generate_single_value(field.type, fake)
                unique_values[field.name].add(value)

            generated_values[field.name] = value
        rows.append(generated_values)
    return rows


def get_row_count(table: Table, engine: Engine):
    logger.info("Getting row count for table {}".format(table.name))
    try:
        stmt = sqlalchemy.select(sqlalchemy.func.count()).select_from(table)
        with engine.connect() as conn:
            result = conn.execute(stmt)
            total_count = result.first()[0]

        logger.info("Total rows in table {}: {}".format(table.name, total_count))

        return total_count
    except Exception as e:
        logger.error("Error getting row count for table {}: {}".format(table.name, e))
        raise e


def insert_generated_values(
    table: Table, row_number: int, fields, session: Session
) -> List:
    logger.info("Generating and inserting values")

    fake = Faker()

    values = generate_values(fields, fake, row_number)

    try:
        session.execute(sqlalchemy.insert(table), values)
        session.commit()

        logger.info("Inserted {} rows".format(len(values)))
    except Exception as e:
        logger.error("Error inserting rows: {}".format(e))
        raise e

    return values
