from datetime import datetime
from typing import Any, Dict, List, Optional


def escape_string(value: Any) -> str:
    """Escape values for safe SQL insertion.

    - Treat None or empty string as SQL NULL.
    - Remove NUL characters which break many SQL engines.
    - Normalize CRLF to LF.
    - Double single quotes (including some unicode single-quote variants) so SQL
      string literals aren't terminated early.
    """
    if value is None:
        return "null"

    s = str(value)
    if s == "":
        return "null"

    # Remove NUL bytes which most SQL engines don't accept inside literals
    s = s.replace("\x00", "")

    # Normalize newlines (preserve them; SQL string literals can contain newlines)
    s = s.replace("\r\n", "\n").replace("\r", "\n")

    # Escape ASCII single quote and common unicode single-quote variants
    s = s.replace("'", "''").replace("\u2019", "''").replace("\u2018", "''")

    return f"'{s}'"


def format_date(date_val: Any) -> str:
    """Format date values, returning 'null' for empty or zero dates.

    Accepts datetime objects or strings. Returns SQL NULL for blank/zero dates.
    """
    if date_val is None:
        return "null"

    # Accept actual datetime objects
    if isinstance(date_val, datetime):
        return f"'{date_val.strftime('%Y-%m-%d %H:%M:%S')}'"

    s = str(date_val)
    if s == "" or s == "0000-00-00 00:00:00" or s == "0000-00-00":
        return "null"

    # Wrap and escape any quotes/newlines in the provided string
    return escape_string(s)


def format_value(value: Any, value_type: str) -> str:
    """Format value based on its type."""
    if value_type.lower() == "date" or value_type.lower() == "datetime":
        return format_date(value)
    elif value_type.lower() == "str":
        return escape_string(value)
    elif value_type.lower() in ["int", "bool"]:
        if value is None or value == "":
            return "null"
        return str(value)
    else:
        return escape_string(value)  # Default to string handling


def convert_json_to_insert_sql(
    json_data: List[Dict[str, Any]],
    column_mapping: List[Dict[str, str]],
    target_tablename: str,
) -> str:
    """Convert JSON data to SQL insert statement with multiple VALUES."""

    # Get column names
    columns = [mapping["target"] for mapping in column_mapping]
    columns_sql = ", ".join(columns)

    # Collect all value sets
    all_values = []
    for record in json_data:
        values = []
        for mapping in column_mapping:
            source_field = mapping["source"]
            value_type = mapping["type"]
            value: Any
            try:
                value = mapping["default"]
            except KeyError:
                value = record.get(source_field)
            formatted_value = format_value(value, value_type)
            values.append(formatted_value)
        all_values.append(f"({', '.join(str(value) for value in values)})")

    # Create single INSERT statement with multiple VALUES
    values_sql = ",\n".join(all_values)
    sql_statement = (
        f"INSERT INTO {target_tablename} ({columns_sql})\nVALUES\n{values_sql};"
    )

    return sql_statement


def convert_json_to_update_sql(
    json_data: List[Dict[str, Any]],
    column_mapping: List[Dict[str, str]],
    target_tablename: str,
    source_id: Optional[str] = None,
    target_id: Optional[str] = None,
) -> str:
    """Convert JSON data to SQL update statements."""

    update_statements = []
    for record in json_data:
        # Build SET clause
        set_values = []
        for mapping in column_mapping:
            source_field = mapping["source"]
            target_field = mapping["target"]
            value_type = mapping["type"]
            value: Any
            try:
                value = mapping["default"]
            except KeyError:
                value = record.get(source_field)

            formatted_value = format_value(value, value_type)
            set_values.append(f"{target_field} = {formatted_value}")

        # Create UPDATE statement for each record
        set_clause = ",\n    ".join(set_values)
        update_sql = f"""UPDATE {target_tablename}
                            SET
                                {set_clause}
                            WHERE id = {record[f'{source_id}']};"""
        update_statements.append(update_sql)

    # Join all UPDATE statements
    return "\n\n".join(update_statements)
