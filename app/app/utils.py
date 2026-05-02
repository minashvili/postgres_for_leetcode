import logging

import sqlalchemy

from app.config import Settings

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


def get_db_engine(settings: Settings):
    logger.info("Connecting to DB")
    connection_string = (
        f"postgresql://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )
    try:
        engine = sqlalchemy.create_engine(connection_string)
    except Exception as e:
        logger.error("Error connecting to DB: {}".format(e))
        raise e

    logger.info("Connected to DB successfully")

    return engine
