from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated
from langgraph.graph import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
import os

load_dotenv()

<<<<<<< HEAD


# ---------------- LLM ---------------- #

llm = ChatGroq(
    model="llama-3.3-70b-versatile",   

    api_key=os.getenv("GROQ_API_KEY")
=======
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key='your_api_key'
>>>>>>> 545efb2bb44e502846bf8ba9ef03158ab0530ab1
)

# ---------------- TOOLS ---------------- #

search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Performs arithmetic operations.
    operations: +  -  *  /
    """

    if operation == "+":
        return {"result": first_num + second_num}

    elif operation == "-":
        return {"result": first_num - second_num}

    elif operation == "*":
        return {"result": first_num * second_num}

    elif operation == "/":

        if second_num == 0:
            return {"result": "division by zero error"}

        return {"result": first_num / second_num}

    return {"result": "invalid operation"}


tools = [search_tool, calculator]

llm_with_tools = llm.bind_tools(tools)


# ---------------- STATE ---------------- #

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ---------------- NODES ---------------- #

def chat_node(state: ChatState):

    response = llm_with_tools.invoke(
        state["messages"]
    )

    return {
        "messages": [response]
    }


# ---------------- MEMORY ---------------- #

conn = sqlite3.connect(
    database="chatbot.db",
    check_same_thread=False
)

checkpointer = SqliteSaver(conn=conn)


# ---------------- GRAPH ---------------- #

tool_node = ToolNode(tools)

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_node("tools", tool_node)


graph.add_edge(START, "chat_node")

# if tool is needed -> go to tools node
graph.add_conditional_edges(
    "chat_node",
    tools_condition
)

# after tool executes -> go back to chat_node
graph.add_edge("tools", "chat_node")

graph.add_edge("chat_node", END)


chatbot = graph.compile(
    checkpointer=checkpointer
)


# ---------------- THREAD LIST ---------------- #

def reterieve_all_threads():

    threads = set()

    for checkpoint in checkpointer.list(None):

        threads.add(
            checkpoint.config["configurable"]["thread_id"]
        )

    return list(threads)