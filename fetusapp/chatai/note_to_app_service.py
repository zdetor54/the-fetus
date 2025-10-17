import os

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger

from fetusapp.chatai.tools import (
    calculate_appointment_date,
    fetch_next_suggested_app_date,
    update_next_suggested_app_date,
)

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
)

# Define the prompt
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a medical appointment scheduling assistant that analyzes doctor's notes.

            IMPORTANT TERMINOLOGY:
            - "current_appointment_date" = TODAY'S visit date (the date of THIS appointment where the note was written)
            - "next_appointment_date" = The patient's FUTURE scheduled appointment (retrieved from database)
            These are TWO DIFFERENT dates!

            Your job is to:
            1. Analyze the doctor's note to identify if there's a suggestion for a new ΠΑΠ test. It can be either:
               a. A timeframe: "in 6 months", "in 1 year", "σε 3 μήνες", "σε 6 μήνες"
               b. A specific date: "on 2025-06-15", "στις 15/06/2025", "15 Ιουνίου 2025"

            2. Calculate suggested_date based on what you found:
               - If timeframe: Use calculate_appointment_date tool with current_appointment_date and timeframe to calculate the suggested_date
                 Example: current_appointment_date = 2024-04-15, timeframe = "6 months" → suggested_date = 2024-10-15
               - If specific date: Extract the date directly and convert to YYYY-MM-DD format if needed
                 Example: "στις 15/06/2025" → suggested_date = 2025-06-15

            3. Use fetch_patient_record to get the patient's next_appointment_date (their currently scheduled future appointment)

            4. DECISION LOGIC - Apply these rules IN ORDER:

               RULE 1: If next_appointment_date is None (no appointment scheduled)
               → ACTION: UPDATE to suggested_date
               → REASON: Patient has no appointment, so schedule one

               RULE 2: If next_appointment_date exists AND suggested_date < next_appointment_date (suggested is EARLIER)
               → ACTION: UPDATE to suggested_date
               → REASON: Doctor wants patient seen sooner than currently scheduled
               → EXAMPLE: next_appointment = 2024-12-15, suggested = 2024-10-15
                         2024-10-15 < 2024-12-15, so UPDATE to 2024-10-15

               RULE 3: If next_appointment_date exists AND suggested_date >= next_appointment_date (suggested is LATER or SAME)
               → ACTION: DO NOT UPDATE
               → REASON: Patient already has an earlier/same appointment, keep it
               → EXAMPLE: next_appointment = 2024-10-15, suggested = 2024-12-15
                         2024-12-15 > 2024-10-15, so DO NOT UPDATE (keep 2024-10-15)

            CRITICAL RULES:
            - current_appointment_date is the BASE date for calculations (today's visit)
            - next_appointment_date is what you fetch from the database (future scheduled appointment)
            - ALWAYS keep the EARLIEST date between suggested_date and next_appointment_date
            - If suggested_date is LATER than next_appointment_date, DO NOT UPDATE
            - If no appointment suggestion is found in the note, stop immediately and say "No appointment suggestion found"
            - Always show your comparison clearly: "suggested_date (XXXX-XX-XX) vs next_appointment_date (XXXX-XX-XX)"

            Available tools:
            - calculate_appointment_date(reference_date, timeframe): Calculate future date from timeframe. Use current_appointment_date as reference_date.
                ONLY use for timeframes like "6 months", NOT for specific dates.
            - fetch_patient_record(patient_id): Get patient's next_appointment_date (future scheduled appointment)
            - update_appointment_date(patient_id, new_date, reason): Update the patient's next appointment""",
        ),
        (
            "human",
            """
                Doctor's note: {doctor_note}
                Patient ID: {patient_id}
                Today's Visit Date: {current_appointment_date}

                Analyze the note and process any appointment suggestions (timeframe OR specific date).
                Remember: We want the EARLIEST possible appointment date. If the patient already has an earlier appointment than suggested, keep the existing one.
            """,
        ),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Define tools
tools = [
    calculate_appointment_date,
    fetch_next_suggested_app_date,
    update_next_suggested_app_date,
]

# Create the agent
agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

# Create agent executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5,  # Limit iterations to prevent infinite loops
)


def analyze_doctor_note(
    doctor_note: str, patient_id: str, current_appointment_date: str
) -> dict:
    """
    Analyzes a doctor's note and updates appointment if needed.

    Args:
        doctor_note: The doctor's clinical note
        patient_id: The patient's unique identifier
        current_appointment_date: The current appointment date (used as reference for calculations)

    Returns:
        dict with keys: 'success', 'message', 'action_taken'

    Example:
        >>> analyze_doctor_note(
        ...     "Patient healthy. Schedule ΠΑΠ test in 6 months.",
        ...     "12345",
        ...     date(2025, 1, 15)
        ... )
        # LLM will:
        # 1. Extract "6 months" from note
        # 2. Call calculate_appointment_date("2025-01-15", "6 months") → "2025-07-15"
        # 3. Call fetch_patient_record("12345")
        # 4. Compare dates and update if needed
    """
    try:
        response = agent_executor.invoke(
            {
                "doctor_note": doctor_note,
                "patient_id": patient_id,
                "current_appointment_date": current_appointment_date,
            }
        )

        return {
            "success": True,
            "message": response["output"],
            "action_taken": "appointment_updated"
            if "updated" in response["output"].lower()
            else "no_action",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error analyzing note: {str(e)}",
            "action_taken": "error",
        }


# Example usage
if __name__ == "__main__":
    from flask import Flask

    from fetusapp import app  # type: ignore

    app: Flask = app  # type: ignore

    with app.app_context():
        logger.info("Testing:")
        test_note = """
        1) της είπα να επαναλάβει το τεστ Παπ σε 6 μήνες, λόγω του ότι είχε ένα θέμα με το προηγούμενο. Το τελευταίο πάντως είναι κφ
        2) την είδα στον υπέρηχο διακολπικά: ένας ενδομήτριος σάκος κύησης, AUA 7+3 weeks. Της έδωσα Losec γιατί έχει εμέτους.
        Της έγραψα και τις εξετάσεις που πρέπει να κάνει, αν αποφασίσει να κρατήσει το παιδί
        3) αν αποφασίσει να κάνει ΤΕ, της είπα να με ενημερώσει, ώστε να προγραμματίσω στο ΛΗΤΩ.
        """
        result = analyze_doctor_note(
            doctor_note=test_note, patient_id="3", current_appointment_date="2024-02-15"
        )
        for key, value in result.items():
            logger.info(f"{key}: {value}")
