import os
import sqlite3


def insert_records(table: str, db_path: str) -> None:
    """
    Insert records into a table in a SQLite database
    """

    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    assets_dir = os.path.join(parent_dir, "_assets")
    sql_filename = f"{table}.sql"
    sql_path = os.path.join(assets_dir, sql_filename)

    # Establish a connection to the database
    conn = sqlite3.connect(db_path)

    # Create a cursor object using the cursor method
    cursor = conn.cursor()
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split into individual statements
    sql_statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

    # Execute statements in transaction
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        for statement in sql_statements:
            print(f"Executing statement: {statement}")
            cursor.execute(statement)
        conn.commit()
        print(f"Successfully executed {len(sql_statements)} statements")
    except Exception as e:
        conn.rollback()
        print(f"Error executing statements: {str(e)}")
    finally:
        conn.close()


def fetch_records(table: str, db_path: str, limit: int = 5) -> None:
    # Establish a connection to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # For example, to execute a query
    cursor.execute(f"select * from {table} limit {limit}")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    # Don't forget to close the connection
    conn.close()


def delete_records(table: str, db_path: str) -> None:
    # Establish a connection to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # For example, to execute a query
    cursor.execute(f"delete from {table}")
    conn.commit()

    # Don't forget to close the connection
    conn.close()


def get_tables(db_path: str) -> None:
    # Establish a connection to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # For example, to execute a query
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    # Don't forget to close the connection
    conn.close()
