import re
from enum import Enum

from pydantic import BaseModel, model_validator, field_validator
from typing import List


IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,62}$")


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
    nullable: bool = False
    unique: bool = False
    primary_key: bool = False

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return _validate_identifier(v, "field.name")

    @model_validator(mode="after")
    def validate_constraints(self):
        if self.unique and self.nullable:
            raise ValueError(
                "nullable=True is not allowed when unique=True (enforce NOT NULL for UNIQUE)."
            )

        if self.primary_key and self.nullable:
            raise ValueError(
                "primary_key=True is not allowed when nullable=True (PRIMARY KEY implies NOT NULL)."
            )

        return self


class CreateTablePayload(BaseModel):
    table_name: str
    fields: List[Field]
    force_recreate_table: bool = False

    @field_validator("table_name")
    @classmethod
    def validate_table_name(cls, v: str) -> str:
        return _validate_identifier(v, "table_name")

    @model_validator(mode="after")
    def validate_fields(self):
        names = [f.name for f in self.fields]
        if len(names) != len(set(names)):
            raise ValueError("fields[].name must be unique within the request.")

        pk_count = sum(1 for f in self.fields if f.primary_key)
        if pk_count > 1:
            raise ValueError("Only one primary_key field is supported in this version.")

        return self


class GeneratePayload(BaseModel):
    table_name: str
    row_number: int = 10

    @field_validator("table_name")
    @classmethod
    def validate_table_name(cls, v: str) -> str:
        return _validate_identifier(v, "table_name")


def _validate_identifier(value: str, what: str) -> str:
    v = value.strip()
    if not IDENT_RE.fullmatch(v):
        raise ValueError(
            f"{what} must match regex {IDENT_RE.pattern} and be <= 63 chars "
            "(letters/digits/underscore; must not start with a digit)."
        )
    return v


class LeetCodeTablePayload(BaseModel):
    sql_query: str
