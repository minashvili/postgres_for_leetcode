from unittest.mock import MagicMock

import pytest


from fill_data_webapp.models import FieldType


def test_generate_single_value_int(faker):
    from fill_data_webapp.data_content_utils import generate_single_value

    result_value = generate_single_value(FieldType.integer, faker)
    assert type(result_value) is int


def test_generate_single_value_email(faker):
    from fill_data_webapp.data_content_utils import generate_single_value

    result_value = generate_single_value(FieldType.email, faker)
    assert type(result_value) is str
    assert "@" in result_value
    assert "." in result_value


def test_generate_single_value_date(faker):
    from fill_data_webapp.data_content_utils import generate_single_value

    result_value = generate_single_value(FieldType.date, faker)
    assert type(result_value) is str
    assert len(result_value.split("-")) == 3


def test_generate_single_value_float(faker):
    from fill_data_webapp.data_content_utils import generate_single_value

    result_value = generate_single_value(FieldType.float, faker)
    assert type(result_value) is float


def test_generate_single_value_multistring(faker):
    from fill_data_webapp.data_content_utils import generate_single_value

    result_value = generate_single_value(FieldType.text, faker)
    assert type(result_value) is str


def test_generate_single_value_random_type(faker):
    from fill_data_webapp.data_content_utils import generate_single_value

    result_value = generate_single_value("test", faker)
    assert type(result_value) is str


def test_generate_values_success(faker):
    from fill_data_webapp.data_content_utils import generate_values
    from fill_data_webapp.models import Field

    fields = [
        Field(name="id", type=FieldType.integer, primary_key=True),
        Field(name="email", type=FieldType.email, nullable=False),
        Field(name="created_at", type=FieldType.date, nullable=False),
        Field(name="score", type=FieldType.float, nullable=False),
        Field(name="description", type=FieldType.text, nullable=False),
        Field(name="username", type="string", nullable=False),
    ]
    row_number = 10

    result_rows = generate_values(fields, faker, row_number)
    assert len(result_rows) == row_number
    for row in result_rows:
        assert len(row) == len(fields)

    assert len(set(r["id"] for r in result_rows)) == row_number  # unique primary key
    assert type(result_rows[0]["id"]) is int
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


def test_generate_values_unique_constraint():
    from fill_data_webapp.data_content_utils import generate_values
    from fill_data_webapp.models import Field

    mocked_faker = MagicMock()
    mocked_faker.word.side_effect = [
        "unique_value_1",
        "unique_value_1",
        "unique_value_2",
    ]

    fields = [Field(name="username", type="string", unique=True, nullable=False)]
    row_number = 2

    result_rows = generate_values(fields, mocked_faker, row_number)
    assert result_rows == [
        {"username": "unique_value_1"},
        {"username": "unique_value_2"},
    ]
    assert (
        mocked_faker.word.call_count == 3
    )  # Called extra time due to uniqueness retry


def test_generate_values_nullable(faker):
    from fill_data_webapp.data_content_utils import generate_values
    from fill_data_webapp.models import Field

    fields = [Field(name="username", type="string", nullable=True)]
    row_number = 10_000

    result_rows = generate_values(fields, faker, row_number)
    assert len(result_rows) == row_number
    values = [value["username"] for value in result_rows]
    assert None in values


def test_generate_values_not_nullable(faker):
    from fill_data_webapp.data_content_utils import generate_values
    from fill_data_webapp.models import Field

    fields = [Field(name="username", type="string", nullable=False)]
    row_number = 10_000

    result_rows = generate_values(fields, faker, row_number)
    assert len(result_rows) == row_number
    values = [value["username"] for value in result_rows]
    assert None not in values


def test_generate_values_empty_list(faker):
    from fill_data_webapp.data_content_utils import generate_values

    with pytest.raises(ValueError) as excinfo:
        generate_values([], faker, 10)
    assert "No fields provided for value generation" in str(excinfo.value)


def test_get_row_count_success(mock_table, mock_engine_success):
    from fill_data_webapp.data_content_utils import get_row_count

    result_count = get_row_count(mock_table, mock_engine_success)

    assert result_count == 42


def test_get_row_count_failure(mock_table, mock_engine_exception):
    from fill_data_webapp.data_content_utils import get_row_count

    with pytest.raises(Exception) as excinfo:
        get_row_count(mock_table, mock_engine_exception)
    assert "Mocked error" in str(excinfo.value)


def test_insert_generated_values_success(mock_table, mock_session_success):
    from fill_data_webapp.data_content_utils import insert_generated_values
    from fill_data_webapp.models import Field, FieldType

    row_number = 10

    fields = [
        Field(name="id", type=FieldType.integer, primary_key=True),
        Field(name="email", type=FieldType.email, nullable=False),
    ]

    result_rows = insert_generated_values(
        mock_table, row_number, fields, mock_session_success
    )

    mock_session_success.commit.assert_called_once()
    assert len(result_rows) == row_number
    for row in result_rows:
        assert len(row) == len(fields)

    assert len(set(r["id"] for r in result_rows)) == row_number
    assert type(result_rows[0]["id"]) is int
    assert type(result_rows[0]["email"]) is str and "@" in result_rows[0]["email"]


def test_insert_generated_values_failure_on_execute(mock_table, mock_session_exception):
    from fill_data_webapp.data_content_utils import insert_generated_values
    from fill_data_webapp.models import Field, FieldType

    row_number = 10

    fields = [
        Field(name="id", type=FieldType.integer, primary_key=True),
        Field(name="email", type=FieldType.email),
    ]

    with pytest.raises(Exception) as excinfo:
        insert_generated_values(mock_table, row_number, fields, mock_session_exception)
    assert "Mocked error" in str(excinfo.value)
