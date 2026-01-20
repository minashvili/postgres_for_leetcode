from enum import Enum

from pydantic import BaseModel
from typing import List, Any


class FieldType(str, Enum):
    string = "string"
    text = "text"
    integer = "integer"
    email = "email"
    date = "date"
    float = "float"

    @classmethod
    def _missing_(cls, value):
        if value in {"varchar", "text", "multistring"}:
            return cls.text
        if value in {"int", "integer"}:
            return cls.integer
        return super()._missing_(value)


class Field(BaseModel):
    name: str
    type: FieldType
    nullable: bool = True
    unique: bool = False
    primary_key: bool = False

    def model_post_init(self, context: Any, /) -> None:
        self.nullable = self.nullable and not self.primary_key
        self.unique = self.unique or self.primary_key


class Payload(BaseModel):
    table_name: str
    row_number: int = 10
    fields: List[Field]
    force_recreate_table: bool = False
