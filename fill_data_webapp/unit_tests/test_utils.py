from unittest.mock import MagicMock

import pytest


def test_get_db_conn_success(mocker):
    from fill_data_webapp.utils import get_db_engine
    from fill_data_webapp.config import Settings

    settings = Settings()

    mocker.patch("sqlalchemy.create_engine", MagicMock(return_value="mocked_engine"))

    conn = get_db_engine(settings)
    assert conn is not None


def test_get_db_conn_failure(mocker):
    from fill_data_webapp.utils import get_db_engine
    from fill_data_webapp.config import Settings

    settings = Settings()

    mocker.patch("sqlalchemy.create_engine", side_effect=Exception("Mocked error"))

    with pytest.raises(Exception) as excinfo:
        get_db_engine(settings)
    assert "Mocked error" in str(excinfo.value)
