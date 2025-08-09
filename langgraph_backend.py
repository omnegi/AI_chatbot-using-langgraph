from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph,START,END
from langchain_core.messages import HumanMessage,SystemMessage
from typing import TypedDict,Annotated
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class ChatState(TypedDict):
    message:Annotated[list[BaseMessage],add_messages]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key='AIzaSyDUadmyLHdvYtlDE3f0kug7V-gRqs0x7gc'
)

def chat_node(state:ChatState):
    message=state['message']
    response=llm.invoke(message)
    return {'message':[response]}

checkpointer= MemorySaver()
graph= StateGraph(ChatState)

graph.add_node('chat_node',chat_node)

graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

chatbot=graph.compile(checkpointer=checkpointer)

