from pydantic import BaseModel
from typing import List


class Field(BaseModel):
    name: str
    type: str


class Payload(BaseModel):
    table_name: str
    row_number: int = 10
    fields: List[Field]
