# 🤖 Multi-Agent RAG Research Assistant

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?logo=groq&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6B35?logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

> An intelligent multi-agent AI system that reads your research papers, searches the live web, and remembers you across sessions — all working together to answer questions with accurate citations.

---

## 🎯 What It Does

This is **not just a chatbot**. It's a coordinated team of **4 specialist AI agents** that collaborate to give you the best possible answer:

| Agent | Role | Tool Used |
|-------|------|-----------|
| 🧑‍💼 **Orchestrator** | Decides which agents to activate | LLaMA 3.3 70B |
| 📚 **Researcher** | Reads & analyzes uploaded PDF papers | ChromaDB RAG |
| 🌐 **Web Surfer** | Searches live internet for latest info | Tavily API |
| 🧠 **Memory Keeper** | Remembers you across sessions | JSON persistence |
| ✍️ **Writer** | Synthesizes all inputs into final answer | LLaMA 3.3 70B |

---

## 🏗️ System Architecture
USER QUESTION
                      ↓
      ┌───────────────────────────────┐
      │     🧑‍💼 ORCHESTRATOR AGENT    │
      │   (Decides which agents to    │
      │    involve for this query)    │
      └────┬──────────┬──────────┬───┘
           ↓          ↓          ↓
    📚 RESEARCHER  🌐 WEB    🧠 MEMORY
     (PDF RAG)    SURFER     KEEPER
           ↓          ↓          ↓
      ┌───────────────────────────────┐
      │       ✍️ WRITER AGENT         │
      │  (Synthesizes all inputs into │
      │   one comprehensive answer)   │
      └───────────────┬───────────────┘
                      ↓
          FINAL ANSWER + CITATIONS

---

## ✨ Key Features

- 📄 **Upload any PDF** → Ask questions, get cited answers instantly
- 🔍 **Semantic Search** → Finds info by meaning, not just keywords
- 🌐 **Live Web Search** → Real-time information from the internet
- 🧠 **Persistent Memory** → Remembers your name, project, preferences across sessions
- 📚 **Source Citations** → Every answer cites exact PDF pages + web URLs
- 💬 **Multi-turn Chat** → Maintains full conversation context
- 🎨 **Beautiful Dark UI** → Professional Streamlit dashboard
- 📊 **Live Stats** → Real-time PDF count, chunk count, memory count
- ❌ **Delete PDFs** → Remove individual PDFs from knowledge base
- 💥 **Nuclear Reset** → Wipe everything and start fresh

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | LLaMA 3.3 70B (Groq API) | Reasoning & generation |
| **Embeddings** | all-MiniLM-L6-v2 | Text → 384-dim vectors |
| **Vector DB** | ChromaDB | Semantic search storage |
| **Framework** | LangChain | AI pipeline orchestration |
| **Web Search** | Tavily API | Live internet search |
| **UI** | Streamlit | Web application interface |
| **Language** | Python 3.10+ | Core language |

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- Free API keys from:
  - [Groq Console](https://console.groq.com) — LLM (free tier available)
  - [Tavily](https://tavily.com) — Web search (free tier available)

### 1. Clone the repository
```bash
git clone https://github.com/Niteesh014/multi-agent-rag-assistant.git
cd multi-agent-rag-assistant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your API keys
```bash
export GROQ_API_KEY="your_groq_api_key_here"
export TAVILY_API_KEY="your_tavily_api_key_here"
```

### 4. Run the app
```bash
streamlit run app.py
```

App opens at `http://localhost:8501` 🎉

---

## 🎬 How RAG Works in This Project
Step 1: Upload PDF
↓
Step 2: Split into ~1000 char chunks
↓
Step 3: Convert chunks to 384-dim vectors
↓
Step 4: Store vectors in ChromaDB
↓
Step 5: User asks a question
↓
Step 6: Question converted to vector
↓
Step 7: Find TOP 5 most similar chunks
↓
Step 8: Send chunks + question to LLM
↓
Step 9: Get accurate, cited answer! ✅

---

## 🧪 How to Use

1. **Upload PDFs** → Use the sidebar upload button
2. **Ask anything** → Type in the chat box
3. **Watch agents work** → See which agents activated
4. **Check sources** → Expand "View Sources" for citations
5. **Tell it about yourself** → It will remember you!
6. **Ask web questions** → No PDF needed, it searches live

### Example Questions to Try

📄 PDF Questions:
"What is the main contribution of the uploaded paper?"
"Summarize the methodology section"
"What datasets were used in the experiments?"
🌐 Web Questions:
"What are the latest AI breakthroughs in 2026?"
"What is the current state of LLM research?"
🧠 Personal Questions:
"What's my name?"
"What project am I working on?"
"What did we discuss earlier?"
🔥 Combined:
"Based on my project, what should I learn from these papers?"
"Compare the paper's findings with latest 2026 research"

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| Development Phases | 9 completed ✅ |
| Specialist Agents | 4 + 1 orchestrator |
| Vector Dimensions | 384 |
| LLM Parameters | 70 Billion |
| Chunk Size | 1000 chars (200 overlap) |
| Max PDFs | Unlimited |

---

## 🗂️ Project Structure

multi-agent-rag-assistant/
│
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── multi_agent_rag_assistant.ipynb  # Development notebook
└── .gitignore               # Git ignore rules

---

## 🔑 Environment Variables

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `GROQ_API_KEY` | LLM API key | [console.groq.com](https://console.groq.com) |
| `TAVILY_API_KEY` | Web search API key | [tavily.com](https://tavily.com) |

---

## 🎓 Skills Demonstrated

Building this project taught me and demonstrates:

- ✅ **RAG Pipeline** — from PDF to cited answer end-to-end
- ✅ **Multi-Agent Architecture** — orchestration & specialist patterns
- ✅ **Vector Databases** — embeddings, semantic search, ChromaDB
- ✅ **LLM Engineering** — prompt design, tool routing, temperature tuning
- ✅ **Persistent Memory** — cross-session user context storage
- ✅ **API Integration** — Groq, Tavily, HuggingFace APIs
- ✅ **Production UI** — Streamlit with custom components
- ✅ **Software Engineering** — caching, error handling, state management

---

## 🚧 Future Roadmap

- [ ] Deploy permanently on HuggingFace Spaces
- [ ] Add streaming responses (token by token)
- [ ] Support URLs, DOCX, TXT as input sources
- [ ] Fine-tune embeddings on domain-specific data
- [ ] Add voice input/output
- [ ] Multi-user support with isolated memory
- [ ] REST API endpoint for external integrations
- [ ] Docker containerization

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License — free to use, modify, and distribute for any purpose.

---

## 👨‍💻 About the Author

**Niteesh Kumar**
- 🎓 Final Year Data Science Student
- 💼 Looking for AI/ML internships & jobs abroad
- 🌐 [LinkedIn](https://www.linkedin.com/in/niteesh-kumar-444b162a8/)
- 🐙 [GitHub](https://github.com/Niteesh014)
- 📧 Available for collaboration and opportunities

---

## ⭐ Support

If you found this project useful or interesting:
- ⭐ **Star this repo** — it helps others discover it!
- 🍴 **Fork it** — build something awesome on top!
- 📢 **Share it** — spread the word!

---
