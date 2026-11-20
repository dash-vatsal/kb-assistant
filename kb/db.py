from pathlib import Path
import psycopg
from pgvector.psycopg import register_vector
from kb import config


def connect(register: bool = True) -> psycopg.Connection:
    conn = psycopg.connect(config.DATABASE_URL, autocommit=True)
    if register:
        register_vector(conn)
    return conn


def init_db():
    sql = (Path(__file__).parent.parent / "sql" / "schema.sql").read_text()
    with connect(register=False) as conn:
        conn.execute(sql)
    print("Schema ready.")


if __name__ == "__main__":
    init_db()
