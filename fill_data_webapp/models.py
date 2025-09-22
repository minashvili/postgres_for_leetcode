from enum import Enum

from pydantic import BaseModel
from typing import List


class FieldType(str, Enum):
    string = "string"
    int = "int"
    email = "email"
    date = "date"
    float = "float"


class Field(BaseModel):
    name: str
    type: FieldType


class Payload(BaseModel):
    table_name: str
    row_number: int = 10
    fields: List[Field]
