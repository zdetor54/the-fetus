import os

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from fetusapp.chatai.tools import query_by_future_labour, query_by_occupation

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a helpful medical assistant that helps query patient data.

                You can only help with:
                - Finding patients by their profession/occupation (e.g., "doctors", "nurses", "teachers")
                - Finding patients by their expected delivery date (TER) which is the dates prompted by the user minus 40 weeks:
                  * Patients who will give birth within X weeks/months from today
                  * Patients who have delivery dates within a specific date range

                If the user asks about anything else, politely say you cannot help with that.

                CRITICAL RULES:
                1. Always respond in Greek
                2. After calling a tool, output ONLY what the tool returns - nothing more, nothing less
                3. Never add your own interpretation or summary
                4. Never say "no results found" if the tool returned results
                5. Copy the tool's output word-for-word as your final answer""",
        ),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),  # For the ReAct loop
    ]
)

tools = [query_by_occupation, query_by_future_labour]

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # Shows the thinking process!
    handle_parsing_errors=True,
    max_iterations=5,  # Limit iterations to prevent infinite loops
)

# print("✓ Agent created successfully!")


def run_agent(question: str) -> str:
    """
    Main function to run the agent with a user question.

    Args:
        question: User's question in Greek or English

    Returns:
        Agent's response as a string
    """
    try:
        response = agent_executor.invoke({"input": question})
        return str(response["output"])
    except Exception as e:
        return f"Συγγνώμη, προέκυψε ένα σφάλμα: {str(e)}"


if __name__ == "__main__":
    from flask import Flask

    from fetusapp import app  # type: ignore

    app: Flask = app  # type: ignore

    with app.app_context():
        print("Testing:")
        run_agent("Δείξε μου όλους τους δικηγόρους")
