from db import get_connection


def init_db():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            with open("schema.sql") as f:
                cur.execute(f.read())
        conn.commit()
        print("Database initialized — users table ready.")
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()