from typing import Any

def escape_string(value: Any) -> str:
    """Escape single quotes and handle null values for SQL strings."""
    if value is None or value == "":
        return 'null'
    return f"'{str(value).replace("'", "''")}'"

def format_date(date_str: str) -> str:
    """Format date strings, returning 'null' for empty or zero dates."""
    if not date_str or date_str == '0000-00-00 00:00:00' or date_str == '0000-00-00':
        return 'null'
    return f"'{date_str}'"

def format_value(value: Any, value_type: str) -> str:
    """Format value based on its type."""
    if value_type.lower() == 'date':
        return format_date(value)
    elif value_type.lower() == 'str':
        return escape_string(value)
    elif value_type.lower() in ['int', 'bool']:
        return str(value) if value is not None else 'null'
    else:
        return escape_string(value)  # Default to string handling