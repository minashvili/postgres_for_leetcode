from unittest.mock import MagicMock

import pytest


def test_get_db_conn_success(mocker, get_settings):
    from fill_data_webapp.utils import get_db_engine

    mocker.patch("sqlalchemy.create_engine", MagicMock(return_value="mocked_engine"))

    conn = get_db_engine(get_settings)
    assert conn is not None


def test_get_db_conn_failure(mocker, get_settings):
    from fill_data_webapp.utils import get_db_engine

    mocker.patch("sqlalchemy.create_engine", side_effect=Exception("Mocked error"))

    with pytest.raises(Exception) as excinfo:
        get_db_engine(get_settings)
    assert "Mocked error" in str(excinfo.value)
