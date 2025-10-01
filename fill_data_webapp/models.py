from enum import Enum

from pydantic import BaseModel
from typing import List


class FieldType(str, Enum):
    text = "text"
    multistring = "multistring"
    integer = "integer"
    email = "email"
    date = "date"
    float = "float"

    @classmethod
    def _missing_(cls, value):
        if value in {"string", "varchar", "text"}:
            return cls.text
        if value in {"int", "integer"}:
            return cls.integer
        return super()._missing_(value)


class ConstraintType(str, Enum):
    not_null = "not null"
    unique = "unique"
    primary = "primary"


class Field(BaseModel):
    name: str
    type: FieldType
    constraints: List[ConstraintType] = []


class Payload(BaseModel):
    table_name: str
    row_number: int = 10
    fields: List[Field]
    force_recreate_table: bool = False
