from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph,START,END
from langchain_core.messages import HumanMessage,SystemMessage
from typing import TypedDict,Annotated
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
import sqlite3


class ChatState(TypedDict):
    message:Annotated[list[BaseMessage],add_messages]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key='your_api_key'
)

def chat_node(state:ChatState):
    message=state['message']
    response=llm.invoke(message)
    return {'message':[response]}
 
conn=sqlite3.connect(database='chatbot.db',check_same_thread=False)
checkpointer= SqliteSaver(conn=conn)
graph= StateGraph(ChatState)

graph.add_node('chat_node',chat_node)

graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

chatbot=graph.compile(checkpointer=checkpointer)

def reterieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)
  
