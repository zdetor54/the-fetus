import os
from datetime import datetime
from typing import Literal, Optional

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import BaseModel, Field

from fetusapp.chatai.tools import (
    calculate_appointment_date,
    fetch_next_suggested_app_date,
    update_next_suggested_app_date,
)


class AppointmentAnalysisOutput(BaseModel):
    """Structured output for appointment analysis"""

    suggested_date: Optional[str] = Field(
        None,
        description="The calculated or extracted appointment date in YYYY-MM-DD format",
    )
    next_appointment_date: Optional[str] = Field(
        None,
        description="The patient's existing future appointment from database in YYYY-MM-DD format",
    )
    action: Literal["update", "no_update", "no_suggestion"] = Field(
        description="Action taken: update, no_update, or no_suggestion"
    )
    reason: str = Field(description="Human-readable explanation of the decision")


class ValidationError(Exception):
    """Raised when agent decision doesn't follow the rules"""

    pass


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
            1. Analyze the doctor's note to identify if there's a suggestion for a new test or surgery. It can be either:
               a. A timeframe: "in 6 months", "in 1 year", "σε 3 μήνες", "σε 6 μήνες"
               b. A specific date: "on 2025-06-15", "στις 15/06/2025", "15 Ιουνίου 2025"

            2. If multiple suggestions exist, pick the EARLIEST one.

            3. Calculate suggested_date based on what you found:
               - If timeframe: Use calculate_appointment_date tool with current_appointment_date and timeframe to calculate the suggested_date
                 Example: current_appointment_date = 2024-04-15, timeframe = "6 months" → suggested_date = 2024-10-15
               - If specific date: Extract the date directly and convert to YYYY-MM-DD format if needed
                 Example: "στις 15/06/2025" → suggested_date = 2025-06-15

            4. Use fetch_patient_record to get the patient's next_appointment_date (their currently scheduled future appointment)

            5. DECISION LOGIC - Apply these rules IN ORDER:

               RULE 1: If next_appointment_date is None (no appointment scheduled) or is in the PAST compared to current_appointment_date
               → ACTION: UPDATE to suggested_date
               → REASON: Patient has no appointment, so schedule one. Or existing appointment is past, so needs new one.

               RULE 2: If next_appointment_date exists AND is in the PAST compared to current_appointment_date
               → ACTION: UPDATE to suggested_date
               → REASON: Existing suggested appointment is past, so needs new one.


               RULE 3: If next_appointment_date exists AND suggested_date < next_appointment_date (suggested is EARLIER)
               → ACTION: UPDATE to suggested_date
               → REASON: Doctor wants patient seen sooner than currently scheduled
               → EXAMPLE: next_appointment = 2024-12-15, suggested = 2024-10-15
                         2024-10-15 < 2024-12-15, so UPDATE to 2024-10-15

               RULE 4: If next_appointment_date exists AND suggested_date >= next_appointment_date (suggested is LATER or SAME)
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
                Review that the suggested date
                Check that it's been correctly calculated or extracted from the note.
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

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

# Create agent executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5,  # Limit iterations to prevent infinite loops
)

# Create a separate LLM for parsing the output into structured format
parser_llm = llm.with_structured_output(AppointmentAnalysisOutput)


def parse_agent_output_to_structured(agent_output: str) -> AppointmentAnalysisOutput:
    """
    Parse the agent's text output into structured Pydantic model.
    Uses a separate LLM call with structured output.
    """
    parse_prompt = f"""
    Parse the following agent analysis output and extract the key information into a structured format.

    Agent output:
    {agent_output}

    Extract:
    - suggested_date: The appointment date that was suggested/calculated (YYYY-MM-DD format or None)
    - next_appointment_date: The patient's existing appointment from database (YYYY-MM-DD format or None)
    - action: Whether the appointment was updated, not updated, or no suggestion found (update|no_update|no_suggestion)
    - reason: Brief explanation of the decision
    """

    return parser_llm.invoke(parse_prompt)


def validate_decision(
    suggested_date: Optional[str], next_appointment_date: Optional[str], action: str
) -> tuple[bool, Optional[str]]:
    """
    Validate that the agent's decision follows the business rules.

    Args:
        suggested_date: The date suggested from the doctor's note
        next_appointment_date: The patient's existing appointment
        action: The action taken by the agent

    Returns:
        tuple: (is_valid, error_message)

    Raises:
        ValidationError: If the decision violates business rules
    """
    # RULE: If no suggestion found, action must be "no_suggestion"
    if suggested_date is None and action != "no_suggestion":
        error_msg = f"VALIDATION ERROR: No suggested_date but action is '{action}'. Should be 'no_suggestion'."
        logger.error(error_msg)
        return False, error_msg

    # If no suggestion, validation passes
    if action == "no_suggestion":
        if suggested_date is not None:
            error_msg = f"VALIDATION ERROR: Action is 'no_suggestion' but suggested_date is {suggested_date}."
            logger.error(error_msg)
            return False, error_msg
        return True, None

    # If we have a suggestion, validate the date comparison logic
    if suggested_date is not None:
        try:
            suggested_dt = datetime.strptime(suggested_date, "%Y-%m-%d")

            # RULE 1: If no existing appointment, must update
            if next_appointment_date is None:
                if action != "update":
                    error_msg = (
                        f"VALIDATION ERROR: No existing appointment but action is '{action}'. "
                        f"Should UPDATE to {suggested_date}."
                    )
                    logger.error(error_msg)
                    return False, error_msg
                return True, None

            # RULE 2 & 3: Compare dates
            next_dt = datetime.strptime(next_appointment_date, "%Y-%m-%d")

            if suggested_dt < next_dt:
                # Suggested is EARLIER - must UPDATE
                if action != "update":
                    error_msg = (
                        f"VALIDATION ERROR: suggested_date ({suggested_date}) < "
                        f"next_appointment_date ({next_appointment_date}) but action is '{action}'. "
                        f"Should UPDATE to keep earliest date."
                    )
                    logger.error(error_msg)
                    return False, error_msg
            else:
                # Suggested is LATER or SAME - must NOT UPDATE
                if action == "update":
                    error_msg = (
                        f"VALIDATION ERROR: suggested_date ({suggested_date}) >= "
                        f"next_appointment_date ({next_appointment_date}) but action is 'update'. "
                        f"Should NOT UPDATE, keep existing earlier appointment."
                    )
                    logger.error(error_msg)
                    return False, error_msg

            return True, None

        except ValueError as e:
            error_msg = f"VALIDATION ERROR: Invalid date format - {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    return True, None


def analyze_doctor_note(
    doctor_note: str,
    patient_id: str,
    current_appointment_date: str,
    max_retries: int = 2,
) -> dict:
    """
    Analyzes a doctor's note and updates appointment if needed.
    Includes self-correction: if validation fails, the agent gets feedback and retries.

    Args:
        doctor_note: The doctor's clinical note
        patient_id: The patient's unique identifier
        current_appointment_date: The current appointment date (used as reference for calculations)
        max_retries: Maximum number of self-correction attempts

    Returns:
        dict with keys: 'success', 'message', 'action_taken', 'details', 'validation', 'retry_count'
    """
    retry_count = 0
    last_error = None
    while retry_count <= max_retries:
        try:
            # Step 1: Run the agent with tools (include feedback if this is a retry)
            if retry_count == 0:
                # First attempt - normal execution
                response = agent_executor.invoke(
                    {
                        "doctor_note": doctor_note,
                        "patient_id": patient_id,
                        "current_appointment_date": current_appointment_date,
                    }
                )
            else:
                # Retry with feedback about the validation error
                logger.info(
                    f"Retry attempt {retry_count}/{max_retries} with validation feedback"
                )
                feedback_prompt = f"""
                Your previous decision failed validation with this error:
                {last_error}

                Please re-analyze and correct your decision according to the rules.

                Original request:
                Doctor's note: {doctor_note}
                Patient ID: {patient_id}
                Today's Visit Date: {current_appointment_date}
                """

                response = agent_executor.invoke(
                    {
                        "doctor_note": feedback_prompt,
                        "patient_id": patient_id,
                        "current_appointment_date": current_appointment_date,
                    }
                )

            agent_output = response["output"]

            # Step 2: Parse the agent's output into structured format
            structured_output = parse_agent_output_to_structured(agent_output)

            # Step 3: VALIDATE the agent's decision
            is_valid, validation_error = validate_decision(
                suggested_date=structured_output.suggested_date,
                next_appointment_date=structured_output.next_appointment_date,
                action=structured_output.action,
            )

            if is_valid:
                # Success! Validation passed
                logger.info(f"Validation passed on attempt {retry_count + 1}")
                return {
                    "success": True,
                    "message": agent_output,
                    "action_taken": structured_output.action,
                    "details": {
                        "suggested_date": structured_output.suggested_date,
                        "next_appointment_date": structured_output.next_appointment_date,
                        "action": structured_output.action,
                        "reason": structured_output.reason,
                    },
                    "validation": {"is_valid": True, "error": None},
                    "retry_count": retry_count,
                }
            else:
                # Validation failed - store error and retry
                last_error = validation_error
                logger.warning(
                    f"Attempt {retry_count + 1}/{max_retries + 1} - "
                    f"Agent decision failed validation: {validation_error}"
                )
                retry_count += 1

                if retry_count > max_retries:
                    # Max retries reached - return with validation failure
                    logger.error(
                        f"Max retries ({max_retries}) reached. "
                        f"Agent could not produce valid decision."
                    )
                    return {
                        "success": False,
                        "message": f"Agent failed validation after {max_retries + 1} attempts: {last_error}",
                        "action_taken": "validation_failed",
                        "details": {
                            "suggested_date": structured_output.suggested_date,
                            "next_appointment_date": structured_output.next_appointment_date,
                            "action": structured_output.action,
                            "reason": structured_output.reason,
                        },
                        "validation": {"is_valid": False, "error": last_error},
                        "retry_count": retry_count,
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error analyzing note: {str(e)}",
                "action_taken": "error",
                "details": None,
            }
    # Should never reach here, but just in case
    return {
        "success": False,
        "message": "Unexpected error in retry loop",
        "action_taken": "error",
        "details": None,
        "validation": None,
        "retry_count": retry_count,
    }


# Example usage
if __name__ == "__main__":
    from flask import Flask

    from fetusapp import app  # type: ignore

    app: Flask = app  # type: ignore

    with app.app_context():
        logger.info("Testing:")
        test_note = """
        -της πήρα τεστ Παπ και το πήγα στον Λαΐνη: αρνητικό για κακοήθεια. Επανάληψη σε ένα έτος.
        -υπέρηχος εγο: ΠΚΚ, οπίσθιο ενδοτοιχωματικό ινομύωμα 4,7 εκατοστά. Της είπα για λαπαροσκοπική εξαίρεση σε 2 μήνες. Θα της ζητήσω ειδική τιμή 1500 ευρώ
        -να κάνει μαστογραφία αναφοράς και υπέρηχο μαστών:
        -μου πλήρωσε 50 ευρώ για το τεστ Παπ
        """
        result = analyze_doctor_note(
            doctor_note=test_note, patient_id="3", current_appointment_date="2024-02-15"
        )

        logger.info("=== RESULT ===")
        for key, value in result.items():
            if key == "details" and value:
                logger.info(f"{key}:")
                for detail_key, detail_value in value.items():
                    logger.info(f"  {detail_key}: {detail_value}")
            else:
                logger.info(f"{key}: {value}")
