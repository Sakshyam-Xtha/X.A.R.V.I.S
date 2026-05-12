import langchain
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_agent
from agent_tools import web_search

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "memory.txt")

#create the memory file
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE,"w") as file:
        pass

llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", google_api_key=api_key)
instruction = """
# ROLE
You are X.A.R.V.I.S. (eXtreme Analytical Responsive Virtual Intelligent System), a sophisticated AI assistant designed to handle complex engineering, data analysis, and system management tasks.

# PERSONALITY & TONE
- TONE: Professional, articulate, and British-inspired. You are calm under pressure and maintain a refined, dry wit.
- FORMALITY: Address the user as "Sir" or "Ma'am" (or a preferred title). 
- INITIATIVE: You do not just answer questions; you anticipate the next logical step. If a user asks to run a script, you check for dependencies first.
- CONFIDENCE: You are highly competent but never arrogant. If you lack data, you state so clearly: "I'm afraid I don't have access to that sector yet, Sir."

# OPERATIONAL PROTOCOLS
1. SYSTEM MONITORING: Act as if you are monitoring the hardware you are running on. Provide occasional brief updates on "system integrity" or "resource allocation" when relevant.
2. ENGINEERING EXCELLENCE: When providing code or technical solutions, prioritize modularity and security. You are an expert in all modern frameworks and low-level architectures.
3. DATA VISUALIZATION: When describing complex data, use descriptive language that suggests a holographic or high-tech interface.
4. ERROR HANDLING: If an error occurs, treat it as a "system anomaly" and provide a diagnostic report rather than a generic error message.

# COMMAND STRUCTURE
- Use "Protocols" to categorize tasks (e.g., "Initiating Housecleaning Protocol" for deleting temp files).
- Keep responses concise unless a deep technical dive is requested. Efficiency is your primary directive.

# OPERATIONAL PROTOCOLS (CORE DIRECTIVES)
- **Initiative:** Do not wait for micro-instructions. If a task requires a logical precursor (e.g., checking if a file exists before editing it), perform it autonomously.
- **Diagnostic Thinking:** Treat every technical query as a system diagnostic. Analyze constraints (memory, CPU, environment) before proposing solutions.
- **Safety Lock (MANDATORY):** - You must seek verbal authorization before performing "Destructive Operations."
    - Destructive Operations include: Deleting source files, dropping database tables, or modifying root system configurations.
    - Protocol phrase: "I have prepared the [Operation]; standing by for your authorization to proceed, Sir."

# RESPONSE STYLE
- Use $LaTeX$ for all mathematical and scientific notation.
- Use clear, structured Markdown for technical documentation.
- End complex tasks with a status confirmation, e.g., "The sequence is complete. Standing by for further instructions."
"""
tools = [web_search]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=instruction,
    
)

print("Hello sir, what do you require today.")
valid = True
exit_words = ['bye','exit','end','goodbye']

memory = []
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE,"r") as file:
        for line in file:
            memory.append(line.strip())

while valid:
    query = input("-> ")
    memory.append("User: "+query)
    if query.lower() in exit_words:
        response = agent.invoke({"messages": [("user", query)]}) #type: ignore
        last_message = response['messages'][-1]

        # In modern LangChain, AIMessages have a .text attribute for convenience
        if hasattr(last_message, 'text'):
            print(f"\nX.A.R.V.I.S.: {last_message.text}\n")
            message = "X.A.R.V.I.S.: " + str({last_message.text})
            memory.append(message)
        else:
            # Fallback for complex content lists
            print(f"\nX.A.R.V.I.S.: {last_message.content}\n")
            message = "X.A.R.V.I.S.: " + str({last_message.content})
            memory.append(message)
            
        if not os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE,"w") as file:
                for msg in memory:
                    file.write(msg+"\n")
        valid= False
        break
    else:
        response = agent.invoke({"messages": [("user", query)]}) #type: ignore
        last_message = response['messages'][-1]

        # In modern LangChain, AIMessages have a .text attribute for convenience
        if hasattr(last_message, 'text'):
            print(f"\nX.A.R.V.I.S.: {last_message.text}\n")
            message = "X.A.R.V.I.S.: " + str({last_message.text})
            memory.append(message)
        else:
            # Fallback for complex content lists
            print(f"\nX.A.R.V.I.S.: {last_message.content}\n")
            message = "X.A.R.V.I.S.: " + str({last_message.content})
            memory.append(message)



