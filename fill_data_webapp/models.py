from enum import Enum

from pydantic import BaseModel
from typing import List


class FieldType(str, Enum):
    string = "string"
    varchar = "varchar"
    multistring = "multistring"
    int = "int"
    email = "email"
    date = "date"
    float = "float"


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
