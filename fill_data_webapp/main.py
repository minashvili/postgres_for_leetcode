import logging

from fastapi import FastAPI, HTTPException
import uvicorn

import fill_data_webapp.models as models
import fill_data_webapp.utils as utils
from fill_data_webapp.config import settings


app = FastAPI()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


@app.post("/generate")
def generate_data(payload: models.Payload):
    conn = utils.get_db_conn(settings)
    cur = conn.cursor()

    existing_columns = utils.get_existing_columns_in_db(payload.table_name, cur)

    if not utils.columns_match(existing_columns, payload.fields):
        if payload.force_recreate_table:
            utils.drop_table_if_exists(payload.table_name, conn, cur)
        else:
            raise HTTPException(
                500,
                "Table already exists with different schema. Use force_recreate_table to drop and recreate.",
            )

    columns_def = utils.get_columns_definition(payload.fields)
    utils.create_table_if_not_exists(payload.table_name, columns_def, conn, cur)
    insert_sql = utils.get_insert_query(payload.fields, payload.table_name)

    inserted_rows = utils.insert_generated_values(
        payload.row_number, payload.fields, insert_sql, cur, conn
    )

    total_count = utils.get_row_count(payload.table_name, cur)

    cur.close()
    conn.close()

    return {
        "inserted": len(inserted_rows),
        "total_in_table": total_count,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
