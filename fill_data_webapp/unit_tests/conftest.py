import pytest
from faker import Faker
import os
from unittest import mock

from unittest.mock import MagicMock, Mock

import sqlalchemy

from sqlalchemy import Table, Column, Integer
from sqlalchemy.orm import Session


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


@pytest.fixture
def mock_session_success():
    mock_session = Mock(spec=Session)
    mock_session.execute.return_value = None
    mock_session.commit.return_value = None
    return mock_session


@pytest.fixture
def mock_session_exception():
    mock_session = Mock(spec=Session)
    mock_session.execute.side_effect = Exception("Mocked error")
    mock_session.commit.return_value = None
    return mock_session


def get_mock_table():
    mock_table = Mock(spec=Table)
    mock_table.name = "dummy_table"
    mock_table._annotations = []

    dummy_column = Mock(spec=Column)
    dummy_column.name = "dummy_column"
    dummy_column.type = Integer
    mock_table.columns = [dummy_column]

    return mock_table


@pytest.fixture
def mock_table():
    return get_mock_table()


@pytest.fixture
def get_settings():
    from fill_data_webapp.config import Settings

    return Settings()


@pytest.fixture
def mock_metadata_success():
    mock_metadata = Mock(spec=sqlalchemy.MetaData)
    mock_metadata.schema = None
    mock_metadata.tables = {"dummy_table": get_mock_table()}
    mock_metadata.naming_convention = {}
    mock_metadata.create_all.side_effect = None
    mock_metadata.drop_all.side_effect = None
    return mock_metadata


@pytest.fixture
def mock_metadata_exception():
    mock_metadata = Mock(spec=sqlalchemy.MetaData)
    mock_metadata.schema = None
    mock_metadata.tables = []
    mock_metadata.naming_convention = {}
    mock_metadata.create_all.side_effect = Exception("Mocked error")
    mock_metadata.drop_all.side_effect = Exception("Mocked error")
    return mock_metadata


@pytest.fixture
def mock_engine_success():
    mock_result = Mock()
    mock_result.first.return_value = (42,)

    mock_conn = Mock()
    mock_conn.execute.return_value = mock_result

    cm = MagicMock()
    cm.__enter__.return_value = mock_conn
    cm.__exit__.return_value = None

    mock_engine = Mock(spec=sqlalchemy.Engine)
    mock_engine.connect.return_value = cm
    mock_engine.begin.return_value = cm

    return mock_engine


@pytest.fixture
def mock_engine_exception():
    mock_engine = Mock(spec=sqlalchemy.Engine)
    mock_engine.connect.side_effect = Exception("Mocked error")

    return mock_engine
