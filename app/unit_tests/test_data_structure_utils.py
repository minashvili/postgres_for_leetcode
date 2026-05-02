from unittest.mock import Mock

import pytest
import sqlalchemy

from pydantic import ValidationError
from sqlalchemy import Column, Integer, String, Date, Float, Text, Identity

from app.models import FieldType


def test_create_table_success(mock_engine_success, mock_metadata_success):
    from app.data_structure_utils import create_table

    dummy_table_name = "dummy_table_2"
    dummy_columns = [Mock(spec=sqlalchemy.Column)]

    create_table(
        dummy_table_name, dummy_columns, mock_engine_success, mock_metadata_success
    )
    mock_metadata_success.create_all.assert_called_once()


def test_create_table_if_not_exists_failure(
    mock_engine_success, mock_metadata_exception
):
    from app.data_structure_utils import create_table

    dummy_table_name = "dummy_table"
    dummy_columns = [Mock(spec=sqlalchemy.Column)]

    with pytest.raises(Exception) as excinfo:
        create_table(
            dummy_table_name,
            dummy_columns,
            mock_engine_success,
            mock_metadata_exception,
        )
    assert "Mocked error" in str(excinfo.value)


def test_generate_get_columns_definition_success(get_settings):
    from app.data_structure_utils import get_columns_definition
    from app.models import Field

    fields = [
        Field(name="id", type="int", primary_key=True),
        Field(name="email", type=FieldType.email, nullable=True),
        Field(name="created_at", type=FieldType.date, nullable=True),
        Field(name="score", type=FieldType.float, nullable=True),
        Field(name="description", type="multistring"),
        Field(name="username", type="string", unique=True),
    ]
    expected_columns = [
        Column("id", Integer, Identity(), primary_key=True),
        Column("email", String(get_settings.string_length), nullable=True),
        Column("created_at", Date, nullable=True),
        Column("score", Float, nullable=True),
        Column("description", Text),
        Column("username", String(get_settings.string_length), unique=True),
    ]

    result_rows = get_columns_definition(fields, get_settings)

    for i in range(len(result_rows)):
        assert result_rows[i].name == expected_columns[i].name
        assert str(result_rows[i].type) == str(expected_columns[i].type)
        assert result_rows[i].primary_key == expected_columns[i].primary_key
        assert (
            str(result_rows[i].type) == "Identity"
            or result_rows[i].nullable == expected_columns[i].nullable
        )
        assert result_rows[i].unique == expected_columns[i].unique


def test_create_field_with_wrong_type():
    from app.models import Field

    with pytest.raises(ValidationError):
        Field(name="email", type="unknown_type")


def test_generate_get_columns_definition_empty_list():
    from app.data_structure_utils import get_columns_definition
    from app.config import Settings

    settings = Settings()

    with pytest.raises(ValueError) as excinfo:
        get_columns_definition([], settings)
    assert "No fields provided for columns definition generation" in str(excinfo.value)


def test_get_existing_table_success(mock_table, mock_metadata_success):
    from app.data_structure_utils import get_existing_table

    result_value = get_existing_table("dummy_table", mock_metadata_success)
    assert result_value is not None
    assert result_value.columns[0].name == "dummy_column"
    assert result_value.columns[0].type == Integer


def test_drop_table_success(mock_table, mock_metadata_success, mock_engine_success):
    from app.data_structure_utils import drop_table

    drop_table(mock_table, mock_metadata_success, mock_engine_success)
    mock_metadata_success.drop_all.assert_called_once()


def test_drop_table_error(mock_table, mock_metadata_exception, mock_engine_success):
    from app.data_structure_utils import drop_table

    with pytest.raises(Exception) as excinfo:
        drop_table(mock_table, mock_metadata_exception, mock_engine_success)
    assert "Mocked error" in str(excinfo.value)
