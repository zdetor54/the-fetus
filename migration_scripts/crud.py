import os
import sqlite3


def _split_sql_statements(sql: str) -> list[str]:
    """Yield individual SQL statements, respecting semicolons inside string literals.

    Handles:
      - Single quotes with doubled '' escapes
      - Double quotes (identifiers) with doubled "" escapes
      - Ignores semicolons inside those quoted regions
    Does NOT fully parse comments; simple removal of -- line comments applied.
    """
    # Remove -- line comments (not inside strings)
    cleaned_lines = []
    for line in sql.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("--"):
            continue
        cleaned_lines.append(line)
    sql = "\n".join(cleaned_lines)

    statements = []
    buf = []
    in_single = False
    in_double = False
    i = 0
    length = len(sql)
    while i < length:
        ch = sql[i]
        if ch == "'" and not in_double:
            # Toggle single quote context unless it's an escaped ''
            if in_single and i + 1 < length and sql[i + 1] == "'":
                # Escaped quote inside single-quoted literal
                buf.append("''")
                i += 2
                continue
            in_single = not in_single
            buf.append(ch)
        elif ch == '"' and not in_single:
            if in_double and i + 1 < length and sql[i + 1] == '"':
                buf.append('""')
                i += 2
                continue
            in_double = not in_double
            buf.append(ch)
        elif ch == ";" and not in_single and not in_double:
            statement = "".join(buf).strip()
            if statement:
                statements.append(statement)
            buf = []
        else:
            buf.append(ch)
        i += 1
    # Remainder
    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)
    return statements


def insert_records(table: str, db_path: str) -> None:
    """Insert records from a generated .sql file (supports semicolons inside values)."""
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    assets_dir = os.path.join(parent_dir, "_assets")
    sql_filename = f"{table}.sql"
    sql_path = os.path.join(assets_dir, sql_filename)

    with open(sql_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Prefer executing the full script if only one statement (most of these files)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        statements = _split_sql_statements(sql_content)
        for stmt in statements:
            print(
                f"Executing statement: {stmt[:120]}{'...' if len(stmt) > 120 else ''}"
            )
            cursor.execute(stmt)
        conn.commit()
        print(f"Successfully executed {len(statements)} statements")
    except Exception as e:
        conn.rollback()
        print(f"Error executing statements: {e}")
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
