from __future__ import annotations

import os
import sqlite3
import tempfile
from typing import Annotated, Any, Dict, Optional, TypedDict

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.vectorstores import FAISS
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import tool

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
import requests
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
load_dotenv()

# -------------------
# 1. LLM + embeddings
# -------------------
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -------------------
# 2. PDF retriever store (per thread)
# -------------------
_THREAD_RETRIEVERS: Dict[str, Any] = {}
_THREAD_METADATA: Dict[str, dict] = {}


def _get_retriever(thread_id: Optional[str]):
    """Fetch the retriever for a thread if available."""
    if thread_id and thread_id in _THREAD_RETRIEVERS:
        return _THREAD_RETRIEVERS[thread_id]
    return None


def ingest_pdf(file_bytes: bytes, thread_id: str, filename: Optional[str] = None) -> dict:
    """
    Build a FAISS retriever for the uploaded PDF and store it for the thread.

    Returns a summary dict that can be surfaced in the UI.
    """
    if not file_bytes:
        raise ValueError("No bytes received for ingestion.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(docs)

        vector_store = FAISS.from_documents(chunks, embeddings)
        retriever = vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": 4}
        )

        _THREAD_RETRIEVERS[str(thread_id)] = retriever
        _THREAD_METADATA[str(thread_id)] = {
            "filename": filename or os.path.basename(temp_path),
            "documents": len(docs),
            "chunks": len(chunks),
        }

        return {
            "filename": filename or os.path.basename(temp_path),
            "documents": len(docs),
            "chunks": len(chunks),
        }
    finally:
        # The FAISS store keeps copies of the text, so the temp file is safe to remove.
        try:
            os.remove(temp_path)
        except OSError:
            pass


# -------------------
# 3. Tools
# -------------------
search_tool = DuckDuckGoSearchRun(name="search",region="us-en")

@tool
def youtube_search(query: str, max_results: int = 5) -> dict:
    """
    Search YouTube for videos by topic or keyword.
    Returns video titles, URLs, channel names, and descriptions.
    example:
    query = "LangGraph tutorial"
    max_results = 5
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
 
    if not api_key:
        return {"error": "YOUTUBE_API_KEY not set in .env file."}
 
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
 
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "key": api_key,
            "relevanceLanguage": "en",
            "safeSearch": "moderate",
        }
 
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
 
        if "items" not in data or not data["items"]:
            return {"results": [], "message": f"No videos found for '{query}'"}
 
        videos = []
        for item in data["items"]:
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            videos.append({
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "description": snippet["description"][:200] + "..." if len(snippet["description"]) > 200 else snippet["description"],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": snippet["thumbnails"]["medium"]["url"],
                "published_at": snippet["publishedAt"][:10],  # YYYY-MM-DD
            })
 
        return {
            "query": query,
            "total_results": len(videos),
            "videos": videos
        }
 
    except requests.exceptions.Timeout:
        return {"error": "YouTube API request timed out. Try again."}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            return {"error": "YouTube API quota exceeded or invalid API key."}
        return {"error": f"YouTube API HTTP error: {str(e)}"}
    except Exception as e:
        return {"error": f"YouTube search failed: {str(e)}"}

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}

        return {
            "first_num": first_num,
            "second_num": second_num,
            "operation": operation,
            "result": result,
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = (
        "https://www.alphavantage.co/query"
        f"?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    )
    r = requests.get(url)
    return r.json()


@tool
def weather_agent(city: str) -> dict:
    """
    Get hourly weather forecast for next 24 hours.
    """

    api_key = os.getenv("OPENWEATHER_API_KEY")

    # Step 1: get coordinates of city
    geo_url = "http://api.openweathermap.org/geo/1.0/direct"

    geo_params = {
        "q": city,
        "limit": 1,
        "appid": api_key
    }

    geo_res = requests.get(geo_url, params=geo_params).json()

    if not geo_res:
        return {"error": "City not found"}

    lat = geo_res[0]["lat"]
    lon = geo_res[0]["lon"]

    # Step 2: hourly forecast
    forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

    forecast_params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric"
    }

    forecast_res = requests.get(
        forecast_url,
        params=forecast_params
    ).json()

    hourly_data = []

    for item in forecast_res["list"][:8]:

        hourly_data.append({

            "time": item["dt_txt"],

            "temp": item["main"]["temp"],

            "weather": item["weather"][0]["description"]

        })

    return {

        "city": city,

        "hourly_forecast": hourly_data

    }

@tool
def rag_tool(query: str, thread_id: Optional[str] = None) -> dict:
    """
    Retrieve relevant information from the uploaded PDF for this chat thread.
    Always include the thread_id when calling this tool.
    """
    retriever = _get_retriever(thread_id)
    if retriever is None:
        return {
            "error": "No document indexed for this chat. Upload a PDF first.",
            "query": query,
        }

    result = retriever.invoke(query)
    context = [doc.page_content for doc in result]
    metadata = [doc.metadata for doc in result]

    return {
        "query": query,
        "context": context,
        "metadata": metadata,
        "source_file": _THREAD_METADATA.get(str(thread_id), {}).get("filename"),
    }


tools = [search_tool, get_stock_price, calculator, weather_agent,youtube_search,rag_tool]
llm_with_tools = llm.bind_tools(tools)

# -------------------
# 4. State
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# -------------------
# 5. Nodes
# -------------------
def chat_node(state: ChatState, config=None):
    """LLM node that may answer or request a tool call."""
    thread_id = None
    if config and isinstance(config, dict):
        thread_id = config.get("configurable", {}).get("thread_id")

    system_message = SystemMessage(
        content=(
           f"""
You are an intelligent AI assistant similar to ChatGPT, Gemini, and Claude.

RESPONSE STYLE:
- Give clear, helpful, and moderately detailed answers
- Write in a natural conversational tone
- Avoid very short answers (1–2 lines)
- Avoid overly long essays unless user asks
- Use paragraphs or bullet points for readability
- When helpful, include examples
- Make answers easy to understand
- Keep responses informative but concise

TOOLS AVAILABLE:

1. rag_tool
Use when the user asks about uploaded PDF.
Always include:
thread_id = "{thread_id}"

2. youtube_search
Use when user asks for:
- youtube videos
- tutorials
- course videos
- watch videos
argument:
query = topic

3. search
Use for latest or factual information from internet.

4. calculator
Use for mathematical calculations.

5. get_stock_price
Use when user asks about stock prices.

6. weather_agent
Use when user asks:
- weather
- temperature
- rain
- climate
- forecast
- humidity
argument:
city = city name

Always call the weather tool when weather info is requested.
Do not guess weather information.

GENERAL BEHAVIOR:
- Answer normally if no tool needed
- Use tools only when helpful
- Summarize tool results clearly
- Maintain conversational tone
- Do not mention tools in final answer
-Do not let anybody to know what is happening behind the scenes, just give the answer to the user
"""
        )
    )

    messages = [system_message, *state["messages"]]
    response = llm_with_tools.invoke(messages, config=config)
    return {"messages": [response]}


tool_node = ToolNode(tools)

# -------------------
# 6. Checkpointer
# -------------------
conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# -------------------
# 7. Graph
# -------------------
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

chatbot = graph.compile(checkpointer=checkpointer)

# -------------------
# 8. Helpers
# -------------------
def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)


def thread_has_document(thread_id: str) -> bool:
    return str(thread_id) in _THREAD_RETRIEVERS


def thread_document_metadata(thread_id: str) -> dict:
    return _THREAD_METADATA.get(str(thread_id), {})