import logging

import random
from collections import defaultdict
from datetime import timedelta
from typing import List
from faker import Faker
import sqlalchemy
from sqlalchemy import (
    Engine,
    Table,
)
from sqlalchemy.orm import Session

from fill_data_webapp.config import Settings
from fill_data_webapp.models import Field, FieldType

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


def generate_single_value(field_type: FieldType, fake: Faker, settings: Settings):
    match field_type:
        case FieldType.integer:
            return random.randint(settings.min_int, settings.max_int)
        case FieldType.email:
            return fake.email()
        case FieldType.date:
            return fake.date()
        case FieldType.float:
            return round(
                random.uniform(settings.min_float, settings.max_float),
                settings.float_precision,
            )
        case FieldType.text:
            word_count = random.randint(
                settings.text_min_word_count, settings.text_max_word_count
            )
            return " ".join(fake.words(nb=word_count))

    return fake.word()


def generate_values(
    fields: List[Field], fake: Faker, row_number: int, settings: Settings
):
    if len(fields) == 0:
        raise ValueError("No fields provided for value generation")

    rows = []
    previous_value: defaultdict = defaultdict()
    for _ in range(row_number):
        generated_values = {}
        for field in fields:
            if field.unique:
                if field.type == FieldType.integer:
                    if field.name not in previous_value:
                        previous_value[field.name] = settings.min_int
                    value = previous_value[field.name] + 1
                    previous_value[field.name] = value
                    generated_values[field.name] = value
                    continue
                elif field.type == FieldType.string or field.type == FieldType.text:
                    if field.name not in previous_value:
                        previous_value[field.name] = settings.min_int
                    counter = previous_value[field.name] + 1
                    value = f"dummy_value_{counter}"
                    previous_value[field.name] = counter
                    generated_values[field.name] = value
                    continue
                elif field.type == FieldType.email:
                    if field.name not in previous_value:
                        previous_value[field.name] = settings.min_int
                    counter = previous_value[field.name] + 1
                    value = f"dummy_email_{counter}@dummy.dummy"
                    previous_value[field.name] = counter
                    generated_values[field.name] = value
                    continue
                elif field.type == FieldType.date:
                    if field.name not in previous_value:
                        previous_value[field.name] = settings.min_date
                    value = previous_value[field.name] + timedelta(days=1)
                    previous_value[field.name] = value
                    generated_values[field.name] = value
                    continue

            if field.type == FieldType.integer and field.primary_key:
                continue

            value = generate_single_value(field.type, fake, settings)

            if field.nullable and random.random() < settings.null_probability:
                value = None

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
    table: Table, row_number: int, fields, session: Session, settings: Settings
) -> List:
    logger.info("Generating and inserting values")

    fake = Faker()

    values = generate_values(fields, fake, row_number, settings)

    chunk_values = [
        values[i : i + settings.batch_size]
        for i in range(0, len(values), settings.batch_size)
    ]
    for chunk in chunk_values:
        try:
            session.execute(sqlalchemy.insert(table), chunk)
            session.commit()

            logger.info("Inserted {} rows".format(len(chunk)))
        except Exception as e:
            logger.error("Error inserting rows: {}".format(e))
            raise e

    return values
