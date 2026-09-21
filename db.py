import os

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Open a new connection to the PostgreSQL database.

    Reads DB_HOST / DB_PORT / DB_NAME / DB_USER / DB_PASSWORD from the
    environment (see .env). row_factory=dict_row means query results
    come back as dicts (row["email"]) instead of plain tuples.
    """
    return psycopg.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ.get("DB_NAME", "learnloop"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", ""),
        row_factory=dict_row,
    )