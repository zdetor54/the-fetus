import unicodedata

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
        output += f"- {first_name} {last_name} (Επάγγελμα: {prof})\n"

    return output


# Test only if running directly (not when imported)
if __name__ == "__main__":
    from fetusapp import app

    with app.app_context():
        print("Testing:")
        print(query_by_occupation.invoke({"occupation": "ΔΙΚΗΓΟΡΟΣ"}))
