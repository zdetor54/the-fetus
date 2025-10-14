import unicodedata
from datetime import date, datetime, timedelta

from langchain.tools import tool

from fetusapp import db  # type: ignore[has-type]


def remove_accents(text: str) -> str:
    """Remove Greek stress marks/accents for comparison"""
    nfd = unicodedata.normalize("NFD", text)
    return "".join(char for char in nfd if unicodedata.category(char) != "Mn")


def greek_collate(str1: str, str2: str) -> int:
    """Custom collation: case-insensitive, accent-insensitive"""
    s1 = remove_accents(str1.lower()) if str1 else ""
    s2 = remove_accents(str2.lower()) if str2 else ""
    if s1 == s2:
        return 0
    return -1 if s1 < s2 else 1


@tool
def query_by_occupation(occupation: str) -> str:
    """
    Searches for patients by their occupation.
    Use this when the user asks about specific jobs like doctor (γιατρός),
    nurse (νοσοκόμα), teacher (δάσκαλος), engineer (μηχανικός), etc.

    Args:
        occupation: The job or occupation to search for (e.g., "γιατρός", "νοσοκόμα")

    Returns:
        A formatted string with the list of patients in that occupation
    """
    # Get raw connection from SQLAlchemy
    conn = db.engine.raw_connection()

    # Register custom collation
    conn.create_collation("GREEK_CI", greek_collate)
    cursor = conn.cursor()

    # Query with custom collation and filters
    cursor.execute(
        """
        SELECT id, first_name, last_name, occupation
        FROM patients
        WHERE TRIM(occupation) = ? COLLATE GREEK_CI
        AND is_active = 1
    """,
        (occupation.strip(),),
    )

    results = cursor.fetchall()
    conn.close()

    # Format results
    if not results:
        return f"Δεν βρέθηκαν ασθενείς με επάγγελμα: {occupation}"

    output = f"Βρέθηκαν {len(results)} ασθενής/ασθενείς με επάγγελμα '{occupation}':\n"
    for patient in results:
        id, first_name, last_name, prof = patient
        url = f"http://127.0.0.1:8080/patient/{id}"
        output += f"- [{first_name} {last_name}](<{url}>) (Επάγγελμα: {prof})\n"

    return output


@tool
def query_by_future_labour(
    from_date: date,
    to_date: date,
    weeks: int = 40,
) -> str:
    """
    Searches for patients who have a pregnancy labour date within a specified range.
    Use this when the user asks about patients who are about to have labour within a date range in the future.

    Args:
        from_date: The start date of the range (inclusive)
        to_date: The end date of the range (inclusive)

    Returns:
        A formatted string with the list of patients who have labour within the date range
    """

    # go back 40 weeks
    from_date = from_date - timedelta(weeks=weeks)
    to_date = to_date - timedelta(weeks=weeks)

    # Get raw connection from SQLAlchemy
    conn = db.engine.raw_connection()
    cursor = conn.cursor()

    # Query with custom collation and filters
    cursor.execute(
        """
        SELECT p.id, first_name, last_name, h.ter
        FROM patients p
        INNER JOIN pregnancy_history h
            ON h.patient_id = p.id
            AND p.is_active = 1
            AND h.is_active = 1
        WHERE h.ter BETWEEN ? AND ?
        ORDER BY h.ter ASC
    """,
        (from_date, to_date),
    )

    results = cursor.fetchall()
    conn.close()

    # Format results
    if not results:
        return f"Δεν βρέθηκαν ασθενείς πιθανές ημερομηνίες τοκετού απο {from_date} μέχρι {to_date}"

    output = f"Βρέθηκαν {len(results)} ασθενής/ασθενείς με πιθανές ημερομηνίες τοκετού απο {from_date} μέχρι {to_date}:\n"
    for patient in results:
        id, first_name, last_name, ter = patient
        url = f"http://127.0.0.1:8080/patient/{id}"
        labour_date = datetime.strptime(ter, "%Y-%m-%d").date() + timedelta(weeks=weeks)
        output += (
            f"- [{first_name} {last_name}](<{url}>) (Πιθανή Ημ/νία: {labour_date})\n"
        )

    return output


# Test only if running directly (not when imported)
if __name__ == "__main__":
    from flask import Flask

    from fetusapp import app  # type: ignore

    app: Flask = app  # type: ignore

    with app.app_context():
        print("Testing:")
        print(query_by_occupation.invoke({"occupation": "ΔΙΚΗΓΟΡΟΣ"}))
        print(
            query_by_future_labour.invoke(
                {"from_date": "2024-07-01", "to_date": "2024-07-31"}
            )
        )
