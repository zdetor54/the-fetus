import os

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from fetusapp.chatai.tools import query_by_occupation

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
                - Finding patients by their profession/occupation

                If the user asks about anything else, politely say you cannot help with that.

                IMPORTANT: Always respond in Greek.""",
        ),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),  # For the ReAct loop
    ]
)

tools = [query_by_occupation]

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # Shows the thinking process!
    handle_parsing_errors=True,
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
        return response["output"]
    except Exception as e:
        return f"Συγγνώμη, προέκυψε ένα σφάλμα: {str(e)}"


if __name__ == "__main__":
    from fetusapp import app

    with app.app_context():
        print("Testing:")
        run_agent("Δείξε μου όλους τους δικηγόρους")
