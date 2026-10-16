
import sqlite3

DATABASE = "marketing.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS visitors (
                visitor_id TEXT PRIMARY KEY,
                first_seen TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS touchpoints (
                touchpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                visitor_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                visited_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (visitor_id)
                    REFERENCES visitors(visitor_id)
            )
        """)


def save_visit(visitor_id, channel):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO visitors (visitor_id)
            VALUES (?)
            """,
            (visitor_id,)
        )

        connection.execute(
            """
            INSERT INTO touchpoints (visitor_id, channel)
            VALUES (?, ?)
            """,
            (visitor_id, channel)
        )

def initialize_orders():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                visitor_id TEXT NOT NULL,
                total_amount REAL NOT NULL,
                ordered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (visitor_id)
                    REFERENCES visitors(visitor_id)
            )
        """)


def save_order(visitor_id, total_amount):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO orders (visitor_id, total_amount)
            VALUES (?, ?)
            """,
            (visitor_id, total_amount)
        )
        return cursor.lastrowid

