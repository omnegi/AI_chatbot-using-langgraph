# 🤖 AI Agent with RAG and Tool Calling

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?style=for-the-badge&logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-AI-green?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent-orange?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-LLM-black?style=for-the-badge)
![FAISS](https://img.shields.io/badge/FAISS-VectorDB-purple?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?style=for-the-badge&logo=sqlite)
![Gmail API](https://img.shields.io/badge/Gmail-Integration-red?style=for-the-badge&logo=gmail)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

A powerful **multi-tool AI assistant** built using **LangGraph + Groq (LLaMA 3.3)** capable of reasoning, retrieving knowledge, and interacting with real-world tools like Gmail, weather, search, and more.

---

## 🚀 Features

### 🧠 Core AI Capabilities

- Conversational AI powered by **Groq (LLaMA 3.3)**
- Context-aware responses using **LangGraph**
- Dynamic **tool-calling agent architecture**
- Multi-step reasoning with tool selection

---

### 📄 PDF Intelligence (RAG)

- Upload and analyze PDFs
- Semantic search using **FAISS vector database**
- Ask questions directly from documents
- Context-based intelligent answers

---

### 📧 Gmail AI Integration

- ✉️ AI-generated email drafting
- ✅ Approval-based email sending (safe workflow)
- 📥 Read latest emails
- 🔍 Search emails by keyword

---

### 🎥 YouTube Search Tool

- Fetch relevant videos based on query
- Displays:
  - Thumbnail preview
  - Clickable title
  - Channel name
  - Description

---

### 🌤 Weather Agent

- Real-time weather using OpenWeather API
- Shows:
  - Temperature
  - Weather condition
  - Hourly forecast

---

### 📈 Stock Price Tool

- Get real-time stock data using Alpha Vantage API

---

### 🧮 Calculator Tool

- Perform arithmetic operations:
  - Add, Subtract, Multiply, Divide

---

### 🌐 Web Search

- Real-time search using DuckDuckGo

---

### 💬 Chat Memory

- Maintains conversation history
- Powered by **SQLite + LangGraph checkpointer**
- Enables context-aware multi-turn chat

---

### 💬 Chat Interface

- Built with **Streamlit**
- ChatGPT-like UI
- Tool outputs displayed cleanly
- Interactive chat experience

---

## 🏗 Tech Stack

### Frontend
- Streamlit
- Custom UI styling

### Backend
- Python
- LangGraph
- LangChain
- Groq API (LLaMA 3.3)

### Data & Storage
- SQLite (chat memory)
- FAISS (vector database)

### APIs Used
- Gmail API
- YouTube Data API
- OpenWeather API
- DuckDuckGo Search
- Alpha Vantage API

---

## 📂 Project Structure
project/
│
├── streamlit_frontend.py
├── langgraph_backend.py
├── gmail_tool.py
├── chatbot.db
├── .env
├── credentials.json
├── token.json
└── README.md


---

## ⚙️ Setup Instructions

### 1. Clone repository


git clone https://github.com/your-username/your-repo.git

cd your-repo


---

### 2. Install dependencies


pip install -r requirements.txt


---

### 3. Setup environment variables

Create `.env` file:


GROQ_API_KEY=your_key
YOUTUBE_API_KEY=your_key
OPENWEATHER_API_KEY=your_key


---

### 4. Setup Gmail API

- Enable Gmail API in Google Cloud Console
- Create OAuth Client (Desktop App)
- Download `credentials.json`
- Add your email to **Test Users**

---

### 5. Run application


streamlit run streamlit_frontend.py


---

## 🧪 Example Queries


weather in delhi
latest news in india
youtube python tutorial
summarize this pdf
write email for leave
show my latest emails


---

## 🔐 Email Safety Workflow

- Draft shown before sending
- Requires user approval
- Prevents accidental email sending

---

## 💡 Highlights

- Built **agentic AI system with tool calling**
- Implemented **RAG pipeline with FAISS**
- Integrated **real-world APIs (Gmail, Weather, YouTube)**
- Designed **multi-tool intelligent assistant**
- Created **memory-enabled conversational system**

---

## 🚀 Future Improvements

- Long-term memory (PostgreSQL + pgvector)
- Multi-agent system
- Email auto-reply AI
- Voice assistant integration
- Deployment (Render / Vercel)

---

## 👨‍💻 Author

**Om Negi**

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!
