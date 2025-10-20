import unicodedata
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from langchain.tools import tool

from fetusapp import db  # type: ignore[has-type]
from fetusapp.models import Patient


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


BASE_OCCUPATION_SYNONYMS = {
    # --- Ιατρικά επαγγέλματα ---
    "ιατρός": [
        "ιατρός",
        "γιατρός",
        "γιατροσ",
        "ιατροσ",
        "παιδίατρος",
        "ψυχίατρος",
        "γαστρεντερολογοσ",
        "ωρλ",
        "οδοντίατρος",
        "οδοντοτεχνιτρια",
        "ιατροσ δερματολογοσ",
        "τεχνολογοσ ιατρικων εργαστηριων",
    ],
    "νοσηλεύτρια": ["νοσηλεύτρια", "noσηλεύτρια", "σχολικη νοσηλευτρια"],
    "φυσικοθεραπεύτρια": ["φυσικοθεραπεύτρια", "φυσιοθεραπεύτρια"],
    "βοηθός φαρμακοποιού": ["βοηθός φαρμακοποιού", "σε φαρμακείο"],
    "φαρμακοποιός": ["φαρμακοποιός", "φαρμακευτικη", "συνταξιουχοσ φαρμακοποιοσ"],
    "ψυχολόγος": ["ψυχολόγος", "ψυχοθεραπευτρια", "ψυχίατρος"],
    "οδοντίατρος": ["οδοντίατρος", "οδοντοτεχνιτρια"],
    "δασκάλα": ["δασκάλα", "δασκάλα αγγλικών"],
    "εκπαιδευτικός": ["εκπαιδευτικός", "εκπαιδευτηκοσ", "παιδαγωγοσ"],
    "καθηγήτρια": [
        "καθηγήτρια",
        "καθηγήτρια αγγλικών",
        "καθηγήτρια γαλλικών",
        "καθηγήτρια γερμανικών",
        "καθηγητρια ισπανικων",
    ],
    # --- Επιστημονικά / τεχνικά ---
    "πολιτικός μηχανικός": [
        "πολιτικός μηχανικός",
        "πολιτικοσ μηχανικοσ",
        "μηχανικοσ περιβαλλοντοσ",
        "τοπογράφος μηχανικός",
    ],
    "μηχανικός": ["μηχανικός", "χημικός μηχανικός", "ηλεκτρολόγος μηχανικός"],
    "αρχιτέκτονας": ["αρχιτέκτονας", "αρχιτέκτων", "αρχιτεκτονασ"],
    "οικονομολόγος": ["οικονομολογοσ", "οικονομικα", "οικονομικό πανεπιστήμιο"],
    # --- Ελεύθερα επαγγέλματα ---
    "δικηγόρος": ["δικηγόρος"],
    "δικαστικός": [
        "δικαστικοσ",
        "δικαστής",
        "δικαστικη υπαλληλοσ",
        "δικαστικός υπόλληλος",
        "δικαστικη λειτουργοσ",
        "εισαγγελέας",
    ],
    "δημοσιογράφος": ["δημοσιογράφος", "διαφημίστρια στον δολ"],
    "ηθοποιός": ["ηθοποιός", "ηθοποιοσ casting director"],
    "σχεδιάστρια": ["σχεδιαστρια", "designer", "ενδυματολόγος", "διακοσμήτρια"],
    # --- Υπάλληλοι & υπηρεσίες ---
    "ιδιωτική υπάλληλος": ["ιδιωτική υπάλληλος", "ιδιωτικός υπάλληλος", "ιδ υπαλληλοσ"],
    "δημόσιος υπάλληλος": [
        "δημόσιος υπάλληλος",
        "δημοτικοσ υπαλληλοσ",
        "δημοτική υπάλληλος",
    ],
    "διοικητική υπάλληλος": [
        "διοικητικη υπαλληλοσ",
        "διοικητικη υπαλληλοσ πανεπιστημιο αθηνων",
        "γραμματεασ στο οπα",
        "γραμματεασ πολιτοπουλου",
        "γραμματεασ υγεια (ανδρεου)",
    ],
    "τραπεζικός υπάλληλος": [
        "τραπεζικοσ υπαλληλοσ",
        "τραπεζουπάλληλος",
        "τραπεζικοσ υπαλληλοσ πειραιωσ",
        "εθνική τράπεζα",
    ],
    "υπάλληλος γραφείου": ["υπάλληλος γραφείου", "υπάλληλος οτε"],
    "οικιακά": ["οικιακά", "οικιακή βοηθός", "oikiaka"],
    "μαγειρίσσα": ["μαγειρισσα", "ζαχαροπλαστησ", "ζαχαροπλαστικη"],
    "διοικητική υποστήριξη": ["υποθηκοφυλακείο", "επιμελεια ιασω", "στο υγεια"],
    # --- Φοιτήτριες, σπουδαστές ---
    "φοιτήτρια": [
        "φοιτήτρια",
        "φοιτητρια",
        "σπουδαστρια",
        "φοιτήτρια ψυχολογίας",
        "φοιτήτρια παιδαγωγικής",
        "φοιτήτρια νομικής",
        "φοιτήτρια ιατρικής",
        "φοιτήτρια γεωλογίας",
        "φοιτητριασ",
    ],
    # --- Ελεύθερα επαγγέλματα / επιχειρήσεις ---
    "ελεύθερος επαγγελματίας": ["ελεύθερος επαγγελματίας"],
    "επιχειρηματίας": ["επιχειρηματιασ", "επιχειρηση"],
    "αγρότισσα": ["αγροτισσα", "αγροτικα"],
    "τουριστικά": ["τουριστικα", "ξενοδοχειακα"],
    # --- Συνταξιούχοι & άνεργοι ---
    "συνταξιούχος": ["συνταξιούχος", "συνταξιούχος οτε", "συνταξιούχος αναπηρικη"],
    # --- Διοίκηση, οικονομικά, επιθεώρηση ---
    "διοικητική επιστήμη": ["οικονομικα", "οικονομικό πανεπιστήμιο"],
}


def make_symmetric(mapping: dict) -> dict:
    """Expand a compact synonym mapping so every synonym is a key
    pointing to the full (deduped, stable-sorted) synonym list."""
    out = {}
    for _, vals in mapping.items():
        group = sorted(set(vals), key=str.casefold)
        for v in group:
            out[v] = group
    return out


OCCUPATION_SYNONYMS = make_symmetric(BASE_OCCUPATION_SYNONYMS)


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
    synonyms = OCCUPATION_SYNONYMS.get(occupation.strip(), [occupation.strip()])

    # Get raw connection from SQLAlchemy
    conn = db.engine.raw_connection()

    # Register custom collation
    conn.create_collation("GREEK_CI", greek_collate)
    cursor = conn.cursor()

    # Query with custom collation and filters
    placeholders = ",".join("?" for _ in synonyms)
    cursor.execute(
        f"""
        SELECT id, first_name, last_name, occupation
        FROM patients
        WHERE TRIM(occupation) COLLATE GREEK_CI IN ({placeholders})
        AND is_active = 1
    """,
        tuple(synonyms),
    )

    results = cursor.fetchall()
    conn.close()

    # Format results
    if not results:
        return f"Δεν βρέθηκαν ασθενείς με επάγγελμα: {occupation}"

    output = f"Βρέθηκαν {len(results)} ασθενής/ασθενείς με επάγγελμα '{occupation}':\n"
    for patient in results:
        id, first_name, last_name, prof = patient
        url = f"/patient/{id}"
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
    from_date_ter = from_date - timedelta(weeks=weeks)
    to_date_ter = to_date - timedelta(weeks=weeks)

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
        (from_date_ter, to_date_ter),
    )

    results = cursor.fetchall()
    conn.close()

    # Format results
    if not results:
        return f"Δεν βρέθηκαν ασθενείς πιθανές ημερομηνίες τοκετού απο {from_date} μέχρι {to_date}"

    output = f"Βρέθηκαν {len(results)} ασθενής/ασθενείς με πιθανές ημερομηνίες τοκετού απο {from_date} μέχρι {to_date}:\n"
    for patient in results:
        id, first_name, last_name, ter = patient
        url = f"/patient/{id}"
        labour_date = datetime.strptime(ter, "%Y-%m-%d").date() + timedelta(weeks=weeks)
        output += (
            f"- [{first_name} {last_name}](<{url}>) (Πιθανή Ημ/νία: {labour_date})\n"
        )

    return output


@tool
def query_by_next_suggested_appointment(
    from_date: date,
    to_date: date,
) -> str:
    """
    Searches for patients who have a next suggested appointment date within a specified range.
    Use this when the user asks about patients who should be called back for a new appointment
    (e.g. "Ασθενείς με επαναληπτική επίσκεψη μέσα στον επόμενο μήνα / χρόνο").

    Args:
        from_date: The start date of the range (inclusive)
        to_date: The end date of the range (inclusive)

    Returns:
        A formatted string with the list of patients who have next suggested appointment within the date range
    """

    # Get raw connection from SQLAlchemy
    conn = db.engine.raw_connection()
    cursor = conn.cursor()

    # Query with custom collation and filters
    cursor.execute(
        """
        SELECT id, first_name, last_name, next_suggested_appointment
        FROM patients p
        WHERE  is_active = 1
        AND next_suggested_appointment BETWEEN ? AND ?
        ORDER BY next_suggested_appointment ASC
    """,
        (from_date, to_date),
    )

    results = cursor.fetchall()
    conn.close()

    # Format results
    if not results:
        return f"Δεν βρέθηκαν ασθενείς με προτεινόμενα ραντεβού απο {from_date} μέχρι {to_date}"

    output = f"Βρέθηκαν {len(results)} ασθενής/ασθενείς με προτεινόμενα ραντεβού απο {from_date} μέχρι {to_date}:\n"
    for patient in results:
        id, first_name, last_name, next_suggested_appointment = patient
        url = f"/patient/{id}"
        app_date = datetime.strptime(next_suggested_appointment, "%Y-%m-%d").date()
        output += f"- [{first_name} {last_name}](<{url}>) (Πιθανή Ημ/νία: {app_date})\n"

    return output


@tool
def fetch_next_suggested_app_date(patient_id: str) -> date | None:
    """
    This function fetches a patient's record from the database.
    args:
        patient_id: The unique identifier of the patient
    returns:
        The next appointment date or None if not found
    """
    patient = Patient.query.get(patient_id)
    return patient.next_suggested_appointment if patient else None


@tool
def update_next_suggested_app_date(patient_id: str, new_date: str) -> str:
    """
    This function updates the patient's next suggested appointment date.

    Args:
        patient_id: Patient's unique identifier
        new_date: New appointment date in 'YYYY-MM-DD' format

    Returns:
        Success message or error message
    """
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return f"Error: Patient {patient_id} not found"

        patient.next_suggested_appointment = datetime.strptime(
            new_date, "%Y-%m-%d"
        ).date()
        db.session.commit()

        return f"Appointment updated to {new_date}"
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}"


@tool
def calculate_appointment_date(reference_date: str, timeframe: str) -> str:
    """
    Calculate future appointment date from a reference date and timeframe.

    Args:
        reference_date: Date in 'YYYY-MM-DD' format
        timeframe: Like '3 months', '6 weeks', '1 year', '2 days'

    Returns:
        New date in 'YYYY-MM-DD' format
    """
    start = datetime.strptime(reference_date, "%Y-%m-%d")

    # Parse timeframe (e.g., "3 months" -> amount=3, unit="months")
    parts = timeframe.lower().strip().split()
    amount = int(parts[0])
    unit = parts[1].rstrip("s")  # Handle plural

    # Map unit to relativedelta
    delta_map = {
        "day": relativedelta(days=amount),
        "week": relativedelta(weeks=amount),
        "month": relativedelta(months=amount),
        "year": relativedelta(years=amount),
    }

    result = start + delta_map[unit]
    return str(result.strftime("%Y-%m-%d"))


# Test only if running directly (not when imported)
if __name__ == "__main__":
    from flask import Flask

    from fetusapp import app  # type: ignore

    app: Flask = app  # type: ignore

    with app.app_context():
        print("Testing:")
        # print(query_by_occupation.invoke({"occupation": "ΔΙΚΗΓΟΡΟΣ"}))
        # print(
        #     query_by_future_labour.invoke(
        #         {"from_date": "2024-07-01", "to_date": "2024-07-31"}
        #     )
        # )
        print(
            query_by_next_suggested_appointment.invoke(
                {"from_date": "2025-04-01", "to_date": "2025-04-30"}
            )
        )
