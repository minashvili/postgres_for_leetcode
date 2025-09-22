import logging

from fastapi import FastAPI
import uvicorn

import models
import utils
from config import settings


app = FastAPI()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


@app.post("/generate")
def generate_data(payload: models.Payload):
    conn = utils.get_db_conn(settings)
    cur = conn.cursor()

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
