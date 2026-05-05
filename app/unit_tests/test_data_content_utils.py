from datetime import datetime
from unittest.mock import MagicMock

import pytest
import sqlalchemy.types


def test_generate_single_value_int(faker, get_settings):
    from app.data_content_utils import generate_single_value

    field = sqlalchemy.Column("id", sqlalchemy.types.Integer)
    result_value = generate_single_value(field, faker, get_settings)
    assert type(result_value) is int


def test_generate_single_value_email(faker, get_settings):
    from app.data_content_utils import generate_single_value

    field = sqlalchemy.Column("email", sqlalchemy.types.String)
    result_value = generate_single_value(field, faker, get_settings)
    assert type(result_value) is str
    assert "@" in result_value
    assert "." in result_value


def test_generate_single_value_date(faker, get_settings):
    from app.data_content_utils import generate_single_value

    field = sqlalchemy.Column("test", sqlalchemy.types.Date)
    result_value = generate_single_value(field, faker, get_settings)
    assert type(result_value) is str
    assert len(result_value.split("-")) == 3


def test_generate_single_value_float(faker, get_settings):
    from app.data_content_utils import generate_single_value

    field = sqlalchemy.Column("test", sqlalchemy.types.Float)
    result_value = generate_single_value(field, faker, get_settings)
    assert type(result_value) is float


def test_generate_single_value_multistring(faker, get_settings):
    from app.data_content_utils import generate_single_value

    field = sqlalchemy.Column("test", sqlalchemy.types.Text)
    result_value = generate_single_value(field, faker, get_settings)
    assert type(result_value) is str


def test_generate_values_success(faker, get_settings):
    from app.data_content_utils import generate_values

    fields = [
        sqlalchemy.Column("id", sqlalchemy.types.Integer, primary_key=True),
        sqlalchemy.Column("email", sqlalchemy.types.String, nullable=False),
        sqlalchemy.Column("created_at", sqlalchemy.types.Date, nullable=False),
        sqlalchemy.Column("score", sqlalchemy.types.Float, nullable=False),
        sqlalchemy.Column("description", sqlalchemy.types.Text, nullable=False),
        sqlalchemy.Column("username", sqlalchemy.types.String, nullable=False),
    ]

    row_number = 10
    unique_columns = []

    result_rows = generate_values(
        fields, faker, row_number, get_settings, unique_columns
    )
    assert len(result_rows) == row_number
    for row in result_rows:
        assert len(row) == len(fields) - 1  # identity does not return

    assert type(result_rows[0]["email"]) is str and "@" in result_rows[0]["email"]
    assert (
        type(result_rows[0]["created_at"]) is str
        and len(result_rows[0]["created_at"].split("-")) == 3
    )
    assert type(result_rows[0]["score"]) is float
    assert (
        type(result_rows[0]["description"]) is str
        and len(result_rows[0]["description"].split(" ")) >= 2
    )
    assert type(result_rows[0]["username"]) is str


def test_generate_values_unique_constraint_str(get_settings):
    from app.data_content_utils import generate_values

    mocked_faker = MagicMock()

    fields = [
        sqlalchemy.Column(
            "username", sqlalchemy.types.String, unique=True, nullable=False
        )
    ]
    row_number = 2
    unique_columns = ["username"]

    result_rows = generate_values(
        fields, mocked_faker, row_number, get_settings, unique_columns
    )
    assert result_rows == [
        {"username": "dummy_value_1"},
        {"username": "dummy_value_2"},
    ]
    assert mocked_faker.word.call_count == 0  # Faker is not executed for unique fields


def test_generate_values_unique_constraint_date_int(get_settings):
    from app.data_content_utils import generate_values

    mocked_faker = MagicMock()

    fields = [
        sqlalchemy.Column(
            "counter", sqlalchemy.types.Integer, unique=True, nullable=False
        )
    ]
    row_number = 2
    unique_columns = ["counter"]

    result_rows = generate_values(
        fields, mocked_faker, row_number, get_settings, unique_columns
    )
    assert result_rows == [
        {"counter": 1},
        {"counter": 2},
    ]
    assert mocked_faker.word.call_count == 0  # Faker is not executed for unique fields


def test_generate_values_unique_constraint_date_email(get_settings):
    from app.data_content_utils import generate_values

    mocked_faker = MagicMock()

    fields = [
        sqlalchemy.Column("email", sqlalchemy.types.String, unique=True, nullable=False)
    ]
    row_number = 2
    unique_columns = ["email"]

    result_rows = generate_values(
        fields, mocked_faker, row_number, get_settings, unique_columns
    )
    assert result_rows == [
        {"email": "dummy_email_1@dummy.dummy"},
        {"email": "dummy_email_2@dummy.dummy"},
    ]
    assert mocked_faker.word.call_count == 0  # Faker is not executed for unique fields


def test_generate_values_unique_constraint_date(get_settings):
    from app.data_content_utils import generate_values

    mocked_faker = MagicMock()

    fields = [
        sqlalchemy.Column(
            "start_date", sqlalchemy.types.Date, unique=True, nullable=False
        )
    ]
    row_number = 2
    unique_columns = ["start_date"]

    result_rows = generate_values(
        fields, mocked_faker, row_number, get_settings, unique_columns
    )
    assert result_rows == [
        {"start_date": datetime(2000, 1, 2)},
        {"start_date": datetime(2000, 1, 3)},
    ]
    assert mocked_faker.word.call_count == 0  # Faker is not executed for unique fields


def test_generate_values_nullable(faker, get_settings):
    from app.data_content_utils import generate_values

    fields = [sqlalchemy.Column("username", sqlalchemy.types.String, nullable=True)]
    row_number = 10_000
    unique_columns = []

    result_rows = generate_values(
        fields, faker, row_number, get_settings, unique_columns
    )
    assert len(result_rows) == row_number
    values = [value["username"] for value in result_rows]
    assert None in values


def test_generate_values_not_nullable(faker, get_settings):
    from app.data_content_utils import generate_values

    fields = [sqlalchemy.Column("username", sqlalchemy.types.String, nullable=False)]
    row_number = 10_000
    unique_columns = []

    result_rows = generate_values(
        fields, faker, row_number, get_settings, unique_columns
    )
    assert len(result_rows) == row_number
    values = [value["username"] for value in result_rows]
    assert None not in values


def test_generate_values_empty_list(faker, get_settings):
    from app.data_content_utils import generate_values

    unique_columns = []

    with pytest.raises(ValueError) as excinfo:
        generate_values([], faker, 10, get_settings, unique_columns)
    assert "No fields provided for value generation" in str(excinfo.value)


def test_get_row_count_success(mock_table, mock_engine_success):
    from app.data_content_utils import get_row_count

    result_count = get_row_count(mock_table, mock_engine_success)

    assert result_count == 42


def test_get_row_count_failure(mock_table, mock_engine_exception):
    from app.data_content_utils import get_row_count

    with pytest.raises(Exception) as excinfo:
        get_row_count(mock_table, mock_engine_exception)
    assert "Mocked error" in str(excinfo.value)


def test_insert_generated_values_success(
    mock_table, mock_session_success, get_settings
):
    from app.data_content_utils import insert_generated_values

    row_number = 10

    fields = [
        sqlalchemy.Column("id", sqlalchemy.types.Integer, primary_key=True),
        sqlalchemy.Column("email", sqlalchemy.types.String, nullable=False),
    ]
    mock_table.columns = fields
    unique_columns = []

    result_rows = insert_generated_values(
        mock_table, row_number, mock_session_success, get_settings, unique_columns
    )

    mock_session_success.commit.assert_called_once()
    assert len(result_rows) == row_number
    for row in result_rows:
        assert len(row) == len(fields) - 1  # identity does not return

    assert type(result_rows[0]["email"]) is str and "@" in result_rows[0]["email"]


def test_insert_generated_values_failure_on_execute(
    mock_table, mock_session_exception, get_settings
):
    from app.data_content_utils import insert_generated_values

    row_number = 10

    fields = [
        sqlalchemy.Column("id", sqlalchemy.types.Integer, primary_key=True),
        sqlalchemy.Column("email", sqlalchemy.types.String, nullable=False),
    ]
    mock_table.columns = fields
    unique_columns = ["id"]

    with pytest.raises(Exception) as excinfo:
        insert_generated_values(
            mock_table, row_number, mock_session_exception, get_settings, unique_columns
        )
    assert "Mocked error" in str(excinfo.value)
