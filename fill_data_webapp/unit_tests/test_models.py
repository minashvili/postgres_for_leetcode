import pytest
from pydantic_core import ValidationError

from fill_data_webapp.models import Payload


def test_unique_and_nullable_field_definition(get_settings):
    from fill_data_webapp.models import Field

    with pytest.raises(ValidationError) as excinfo:
        Field(name="username", type="string", unique=True, nullable=True)
    assert (
        "nullable=True is not allowed when unique=True (enforce NOT NULL for UNIQUE)."
        in str(excinfo.value)
    )


def test_nullable_and_primary_key_field_definition(get_settings):
    from fill_data_webapp.models import Field

    with pytest.raises(ValidationError) as excinfo:
        Field(name="username", type="string", nullable=True, primary_key=True)
    assert (
        "primary_key=True is not allowed when nullable=True (PRIMARY KEY implies NOT NULL)."
        in str(excinfo.value)
    )


def test_not_unique_fields(get_settings):
    from fill_data_webapp.models import Field

    with pytest.raises(ValueError) as excinfo:
        Payload(
            table_name="test_table",
            row_number=10,
            fields=[
                Field(name="id", type="integer", primary_key=True),
                Field(name="id", type="string", unique=True),
            ],
        )
    assert "fields[].name must be unique within the request." in str(excinfo.value)


def test_multiple_primary_keys_fields(get_settings):
    from fill_data_webapp.models import Field

    with pytest.raises(ValueError) as excinfo:
        Payload(
            table_name="test_table",
            row_number=10,
            fields=[
                Field(name="id", type="integer", primary_key=True),
                Field(name="name", type="string", primary_key=True),
            ],
        )
    assert "Only one primary_key field is supported in this version." in str(
        excinfo.value
    )


def test_wrong_table_name():
    from fill_data_webapp.models import Payload

    with pytest.raises(ValueError) as excinfo:
        Payload(
            table_name="123invalid-table-name",
            row_number=10,
            fields=[],
        )
    assert (
        "table_name must match regex ^[A-Za-z_][A-Za-z0-9_]{0,62}$ and be <= 63 chars "
        "(letters/digits/underscore; must not start with a digit)."
        in str(excinfo.value)
    )


def test_successful_payload_creation(get_settings):
    from fill_data_webapp.models import Field, FieldType, Payload

    fields = [
        Field(name="id", type=FieldType.integer, primary_key=True),
        Field(name="email", type=FieldType.email, nullable=True),
        Field(name="username", type=FieldType.string, unique=True),
    ]

    payload = Payload(
        table_name="valid_table_name",
        row_number=100,
        fields=fields,
        force_recreate_table=True,
    )

    assert payload.table_name == "valid_table_name"
    assert payload.row_number == 100
    assert payload.fields == fields
    assert payload.force_recreate_table is True
