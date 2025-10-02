from unittest.mock import MagicMock

import pytest
from faker import Faker
import os
from unittest import mock

from pydantic import ValidationError

from fill_data_webapp.models import FieldType


@pytest.fixture
def faker():
    return Faker()


@pytest.fixture(autouse=True)
def set_env_var(monkeypatch):
    with mock.patch.dict(os.environ, clear=True):
        envvars = {
            "POSTGRES_USER": "mocked_postgres_user",
            "POSTGRES_PASSWORD": "mocked_postgres_password",
            "POSTGRES_DB": "mocked_postgres_db",
            "POSTGRES_HOST": "mocked_postgres_host",
        }
        for k, v in envvars.items():
            monkeypatch.setenv(k, v)
        yield


def test_get_db_conn_success(mocker):
    from fill_data_webapp.utils import get_db_conn
    from fill_data_webapp.config import Settings

    settings = Settings()

    mocker.patch("psycopg2.connect", MagicMock(return_value="mocked_connection"))

    conn = get_db_conn(settings)
    assert conn is not None


def test_get_db_conn_failure(mocker):
    from fill_data_webapp.utils import get_db_conn
    from fill_data_webapp.config import Settings

    settings = Settings()

    mocker.patch("psycopg2.connect", side_effect=Exception("Mocked error"))

    with pytest.raises(Exception) as excinfo:
        get_db_conn(settings)
    assert "Mocked error" in str(excinfo.value)


def test_generate_single_value_int(faker):
    from fill_data_webapp.utils import generate_single_value

    result_value = generate_single_value(FieldType.integer, faker)
    assert type(result_value) is int


def test_generate_single_value_email(faker):
    from fill_data_webapp.utils import generate_single_value

    result_value = generate_single_value(FieldType.email, faker)
    assert type(result_value) is str
    assert "@" in result_value
    assert "." in result_value


def test_generate_single_value_date(faker):
    from fill_data_webapp.utils import generate_single_value

    result_value = generate_single_value(FieldType.date, faker)
    assert type(result_value) is str
    assert len(result_value.split("-")) == 3


def test_generate_single_value_float(faker):
    from fill_data_webapp.utils import generate_single_value

    result_value = generate_single_value(FieldType.float, faker)
    assert type(result_value) is float


def test_generate_single_value_multistring(faker):
    from fill_data_webapp.utils import generate_single_value

    result_value = generate_single_value(FieldType.multistring, faker)
    assert type(result_value) is str
    assert len(result_value.split(" ")) >= 2


def test_generate_single_value_random_type(faker):
    from fill_data_webapp.utils import generate_single_value

    result_value = generate_single_value("test", faker)
    assert type(result_value) is str


def test_generate_values_success(faker):
    from fill_data_webapp.utils import generate_values
    from fill_data_webapp.models import Field

    fields = [
        Field(name="id", type=FieldType.integer, constraints=["primary"]),
        Field(name="email", type=FieldType.email),
        Field(name="created_at", type=FieldType.date),
        Field(name="score", type=FieldType.float),
        Field(name="description", type=FieldType.multistring),
        Field(name="username", type="string"),
    ]
    row_number = 10

    result_rows = generate_values(fields, faker, row_number)
    assert len(result_rows) == row_number
    for row in result_rows:
        assert len(row) == len(fields)

    assert len(set(r[0] for r in result_rows)) == row_number  # unique primary key
    assert type(result_rows[0][0]) is int
    assert type(result_rows[0][1]) is str and "@" in result_rows[0][1]
    assert type(result_rows[0][2]) is str and len(result_rows[0][2].split("-")) == 3
    assert type(result_rows[0][3]) is float
    assert type(result_rows[0][4]) is str and len(result_rows[0][4].split(" ")) >= 2
    assert type(result_rows[0][5]) is str


def test_generate_values_unique_constraint():
    from fill_data_webapp.utils import generate_values
    from fill_data_webapp.models import Field

    mocked_faker = MagicMock()
    mocked_faker.word.side_effect = [
        "unique_value_1",
        "unique_value_1",
        "unique_value_2",
    ]

    fields = [Field(name="username", type="string", constraints=["unique"])]
    row_number = 2

    result_rows = generate_values(fields, mocked_faker, row_number)
    assert result_rows == [["unique_value_1"], ["unique_value_2"]]
    assert (
        mocked_faker.word.call_count == 3
    )  # Called extra time due to uniqueness retry


def test_generate_values_not_null_constraint():
    from fill_data_webapp.utils import generate_values
    from fill_data_webapp.models import Field

    fields = [Field(name="username", type="string", constraints=["not null"])]
    row_number = 5

    result_rows = generate_values(fields, Faker(), row_number)
    assert len(result_rows) == row_number
    for row in result_rows:
        assert row[0] is not None


def test_generate_values_empty_list(faker):
    from fill_data_webapp.utils import generate_values

    with pytest.raises(ValueError) as excinfo:
        generate_values([], faker, 10)
    assert "No fields provided for value generation" in str(excinfo.value)


def test_create_table_if_not_exists_success(mocker):
    from fill_data_webapp.utils import create_table_if_not_exists

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None

    create_table_if_not_exists("test_table", "id INT", mock_conn, mock_cursor)
    mock_cursor.execute.assert_called_once()
    assert mock_conn.commit.called


def test_create_table_if_not_exists_failure(mocker):
    from fill_data_webapp.utils import create_table_if_not_exists

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_cursor.execute.side_effect = Exception("Mocked error")
    with pytest.raises(Exception) as excinfo:
        create_table_if_not_exists("test_table", "id INT", mock_conn, mock_cursor)
    assert "Mocked error" in str(excinfo.value)


def test_get_row_count_success():
    from fill_data_webapp.utils import get_row_count

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (42,)

    result_count = get_row_count("test_table", mock_cursor)
    assert result_count == 42


def test_get_row_count_failure():
    from fill_data_webapp.utils import get_row_count

    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = Exception("Mocked error")

    with pytest.raises(Exception) as excinfo:
        get_row_count("test_table", mock_cursor)
    assert "Mocked error" in str(excinfo.value)


def test_generate_get_columns_definition_success():
    from fill_data_webapp.utils import get_columns_definition
    from fill_data_webapp.models import Field

    fields = [
        Field(name="id", type="int", constraints=["primary"]),
        Field(name="email", type=FieldType.email),
        Field(name="created_at", type=FieldType.date),
        Field(name="score", type=FieldType.float),
        Field(name="description", type=FieldType.multistring, constraints=["not null"]),
        Field(name="username", type="string", constraints=["unique"]),
    ]

    result_rows = get_columns_definition(fields)
    assert (
        result_rows
        == "id INTEGER NOT NULL, email TEXT , created_at DATE , score REAL , description TEXT NOT NULL, "
        + "username TEXT UNIQUE, PRIMARY KEY (id)"
    )


def test_create_field_with_wrong_constraint():
    from fill_data_webapp.models import Field

    with pytest.raises(ValidationError):
        Field(name="email", type=FieldType.email, constraints=["unknown_constraint"])


def test_create_field_with_wrong_type():
    from fill_data_webapp.models import Field

    with pytest.raises(ValidationError):
        Field(name="email", type="unknown_type")


def test_generate_get_columns_definition_empty_list():
    from fill_data_webapp.utils import get_columns_definition

    with pytest.raises(ValueError) as excinfo:
        get_columns_definition([])
    assert "No fields provided for columns definition generation" in str(excinfo.value)


def test_get_insert_query_success_one_field():
    from fill_data_webapp.utils import get_insert_query
    from fill_data_webapp.models import Field

    fields = [Field(name="id", type=FieldType.integer)]
    table_name = "test_table"
    expected_query = "INSERT INTO test_table (id) VALUES (%s)"

    result_query = get_insert_query(fields, table_name)
    assert result_query == expected_query


def test_get_insert_query_success_many_fields():
    from fill_data_webapp.utils import get_insert_query
    from fill_data_webapp.models import Field

    fields = [
        Field(name="id", type=FieldType.integer),
        Field(name="email", type=FieldType.email),
        Field(name="created_at", type=FieldType.date),
        Field(name="score", type=FieldType.float),
        Field(name="description", type=FieldType.multistring),
        Field(name="username", type="string"),
    ]
    table_name = "test_table"
    expected_query = (
        "INSERT INTO test_table (id, email, created_at, score, description, username) "
        + "VALUES (%s, %s, %s, %s, %s, %s)"
    )

    result_query = get_insert_query(fields, table_name)
    assert result_query == expected_query


def test_get_insert_query_error_empty_list():
    from fill_data_webapp.utils import get_insert_query

    with pytest.raises(ValueError):
        get_insert_query([], "test_table")


def test_insert_generated_values_success():
    from fill_data_webapp.utils import insert_generated_values
    from fill_data_webapp.models import Field, FieldType

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None

    fields = [
        Field(name="id", type=FieldType.integer, constraints=["primary"]),
        Field(name="email", type=FieldType.email),
    ]
    insert_sql = "INSERT INTO test_table (id, email) VALUES (%s, %s)"
    row_number = 5

    result_rows = insert_generated_values(
        row_number, fields, insert_sql, mock_cursor, mock_conn
    )
    assert len(result_rows) == row_number
    for row in result_rows:
        assert len(row) == len(fields)

    assert len(set(r[0] for r in result_rows)) == row_number
    assert type(result_rows[0][0]) is int
    assert type(result_rows[0][1]) is str and "@" in result_rows[0][1]

    assert mock_cursor.execute.call_count == row_number
    assert mock_conn.commit.called


def test_insert_generated_values_failure_on_execute():
    from fill_data_webapp.utils import insert_generated_values
    from fill_data_webapp.models import Field, FieldType

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("Mocked error")

    fields = [
        Field(name="id", type=FieldType.integer, constraints=["primary"]),
        Field(name="email", type=FieldType.email),
    ]
    insert_sql = "INSERT INTO test_table (id, email) VALUES (%s, %s)"
    row_number = 5

    with pytest.raises(Exception) as excinfo:
        insert_generated_values(row_number, fields, insert_sql, mock_cursor, mock_conn)
    assert "Mocked error" in str(excinfo.value)


def test_get_existing_columns_in_db_success():
    from fill_data_webapp.utils import get_existing_columns_in_db
    from fill_data_webapp.models import FieldType

    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = (("test_field", "text"),)

    result_value = get_existing_columns_in_db("test_table", mock_cursor)
    mock_cursor.execute.assert_called_once()
    assert len(result_value) == 1
    assert result_value[0].name == "test_field"
    assert result_value[0].type == FieldType.text


def test_get_existing_columns_in_db_error():
    from fill_data_webapp.utils import get_existing_columns_in_db

    mock_cursor = MagicMock()
    mock_cursor.fetchall.side_effect = Exception("Mocked error")

    with pytest.raises(Exception) as excinfo:
        get_existing_columns_in_db("test_table", mock_cursor)
    assert "Mocked error" in str(excinfo.value)


def test_columns_match_success():
    from fill_data_webapp.utils import columns_match
    from fill_data_webapp.models import Field, FieldType

    existing = [
        Field(name="username", type=FieldType.text, constraints=["unique"]),
        Field(name="score", type=FieldType.float),
    ]
    new = [
        Field(name="username", type="varchar"),
        Field(name="score", type=FieldType.float),
    ]

    result_value = columns_match(existing, new)
    assert result_value


def test_columns_match_wrong_len():
    from fill_data_webapp.utils import columns_match
    from fill_data_webapp.models import Field, FieldType

    existing = [Field(name="username", type=FieldType.text, constraints=["unique"])]
    new = [
        Field(name="username", type="varchar"),
        Field(name="score", type=FieldType.float),
    ]

    result_value = columns_match(existing, new)
    assert not result_value


def test_columns_match_wrong_type():
    from fill_data_webapp.utils import columns_match
    from fill_data_webapp.models import Field, FieldType

    existing = [
        Field(name="username", type=FieldType.text, constraints=["unique"]),
        Field(name="score", type=FieldType.integer),
    ]
    new = [
        Field(name="username", type="varchar"),
        Field(name="score", type=FieldType.float),
    ]

    result_value = columns_match(existing, new)
    assert not result_value


def test_columns_match_wrong_names():
    from fill_data_webapp.utils import columns_match
    from fill_data_webapp.models import Field, FieldType

    existing = [
        Field(name="username", type=FieldType.text, constraints=["unique"]),
        Field(name="score_score", type=FieldType.float),
    ]
    new = [
        Field(name="username", type="varchar"),
        Field(name="score", type=FieldType.float),
    ]

    result_value = columns_match(existing, new)
    assert not result_value


def test_drop_table_if_exists_success():
    from fill_data_webapp.utils import drop_table_if_exists

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None

    drop_table_if_exists("test_table", mock_conn, mock_cursor)
    mock_cursor.execute.assert_called_once()
    assert mock_conn.commit.called


def test_drop_table_if_exists_error():
    from fill_data_webapp.utils import drop_table_if_exists

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("Mocked error")

    with pytest.raises(Exception) as excinfo:
        drop_table_if_exists("test_table", mock_conn, mock_cursor)
    assert "Mocked error" in str(excinfo.value)
