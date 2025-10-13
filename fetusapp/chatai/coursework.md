Module 1: Understanding the Architecture
Lesson 1.1: What We're Building
Think of your conversational agent as having 3 main layers:
User Question (Natural Language)
         ↓
    [AGENT LAYER] ← Brain that decides what to do
         ↓
    [TOOL LAYER] ← Hands that do the work
         ↓
    [DATABASE LAYER] ← Your existing SQLite/Flask
Lesson 1.2: The Components
1. Agent (The Brain)

Receives user's natural language question
Decides which tool to use (or if it can't help)
Returns formatted answer

2. Tools (The Hands)

Tool #1: Query patients by profession
Tool #2: Query live pregnancies for labour days
Each tool knows how to talk to your database

3. Your Existing Flask API (The Database Interface)

You already have routes like /patients
We'll create new routes or services for the agent to call


Lesson 1.3: How LangChain Fits In
LangChain provides:

Agents: Pre-built logic for deciding which tool to use
Tools: A standard way to define what each tool does
LLM Integration: Connects to Claude/OpenAI to understand natural language
Memory: (Optional) Remember conversation context


Lesson 1.4: The Flow
Here's what happens when a user asks: "Show me all pregnant patients due soon"
1. User sends question to your Flask endpoint
   POST /api/chat  {"question": "Show me all pregnant patients due soon"}

2. Flask passes question to LangChain Agent
   agent.run("Show me all pregnant patients due soon")

3. Agent sends question to LLM (Claude/GPT)
   "Which tool should I use for this question?"

4. LLM responds: "Use the labour_days tool"

5. Agent calls your tool function
   query_labour_days()

6. Tool queries your SQLite database
   SELECT * FROM pregnancies WHERE status='active'...

7. Results flow back:
   Tool → Agent → LLM (formats nicely) → Flask → User

📝 Check Your Understanding:
Before we move to Lesson 2, can you answer these?

What is the agent's main job?
How many tools will we create?
Where does the LLM fit in this architecture?
Will we need to change your existing database schema?

Once you're comfortable with this architecture overview, we'll move to Lesson 2: Setting Up LangChain where I'll show you:

Installing dependencies
Creating your first tool
Connecting to an LLM

Ready to continue, or do you have questions about the architecture?RetryClaude can make mistakes. Please double-check responses.
