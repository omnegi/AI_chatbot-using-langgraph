# 🤖 Multi-Utility AI Assistant

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge\&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?style=for-the-badge\&logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-AI-green?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent-orange?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-LLM-black?style=for-the-badge)
![FAISS](https://img.shields.io/badge/FAISS-VectorDB-purple?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?style=for-the-badge\&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

A powerful AI assistant built using **LangGraph + Groq (LLaMA 3.3)** with multiple integrated tools like PDF analysis, YouTube search, weather forecasting, and more.

---

## 🚀 Features

### 🧠 Core AI Capabilities

* Conversational AI powered by **Groq (LLaMA 3.3)**
* Context-aware responses using **LangGraph**
* Multi-tool reasoning (agent-based system)

---

### 📄 PDF Intelligence (RAG)

* Upload and analyze PDFs
* Semantic search using **FAISS**
* Ask questions directly from documents

---

### 🎥 YouTube Search Tool

* Fetch relevant videos based on query
* Displays:

  * Thumbnail preview
  * Title (clickable)
  * Channel name
  * Description

---

### 🌤 Weather Agent

* Real-time weather data using OpenWeather API
* Displays:

  * Temperature
  * Condition
  * Humidity
  * Wind speed
* 📊 Hourly forecast chart visualization

---

### 🧮 Calculator Tool

* Perform arithmetic operations:

  * Add, Subtract, Multiply, Divide

---

### 🌐 Web Search

* Real-time search using DuckDuckGo

---

### 💬 Chat Memory (Short-Term)

* Maintains conversation context within a session
* Powered by **LangGraph + SQLite checkpointer**
* Enables context-aware multi-turn conversations

---

### 💬 Chat Interface

* Modern UI built with **Streamlit**
* Glassmorphism design
* Chat bubbles like ChatGPT
* Tool outputs rendered as UI cards

---

## 🏗 Tech Stack

### Frontend

* Streamlit
* Matplotlib
* Custom CSS (Glass UI)

### Backend

* LangGraph
* LangChain
* Groq API (LLaMA 3.3)

### Data & Storage

* SQLite (chat history / short-term memory)
* FAISS (PDF vector store)

### APIs Used

* YouTube Data API
* OpenWeather API
* DuckDuckGo Search

---

## 📂 Project Structure

```id="r2w4pj"
project/
│
├── frontend.py
├── langgraph_backend.py
├── chatbot.db
├── memory_index/
├── .env
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone repo

```id="bqb3p1"
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

---

### 2. Install dependencies

```id="tptpd3"
pip install -r requirements.txt
```

---

### 3. Add environment variables

Create `.env` file:

```id="3tj21o"
GROQ_API_KEY=your_key
YOUTUBE_API_KEY=your_key
OPENWEATHER_API_KEY=your_key
```

---

### 4. Run app

```id="pc7kjj"
streamlit run frontend.py
```

---

## 🧪 Example Queries

```id="txpdsg"
weather in delhi
hourly weather in mumbai
python tutorials youtube
summarize this pdf
what is machine learning
```

---

## 💡 Highlights

* Multi-agent AI system using LangGraph
* Combines RAG + tools in a single assistant
* Modern UI similar to ChatGPT
* Real-time API integrations

---

## 👨‍💻 Author

**Om Negi**

---

## ⭐ Support

## If you like this project, give it a ⭐ on GitHub!

