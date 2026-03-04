<p align="center">
  <h1 align="center">🧬 GENESIS HIVE MIND</h1>
  <p align="center">
    <strong>Five AI titans think independently. One consensus emerges.</strong>
  </p>
  <p align="center">
    A locally-hosted, multi-agent AI orchestrator powered by Ollama — featuring autonomous terminal execution, self-healing ReAct loops, and codebase-aware RAG.
  </p>
  <p align="center">
    <a href="https://sharansutrapu.com/">🌐 Website</a> •
    <a href="https://www.linkedin.com/in/sharan-kumar-reddy-sutrapu-34b50519b/">💼 LinkedIn</a> •
    <a href="https://github.com/sharansutrapu">💻 GitHub</a> •
    <a href="https://medium.com/@sharansutrapu">📝 Medium</a>
  </p>
</p>

---

## 🧠 What is Genesis?

**Genesis Hive Mind** is a privacy-first, locally-hosted AI command center that orchestrates multiple LLMs running on your own hardware via [Ollama](https://ollama.com/). No API keys. No cloud. No telemetry. Everything runs on your machine.

Genesis is not just another chatbot wrapper — it is a **multi-agent orchestration framework** with three core capabilities:

---

### 🏛️ The True Council — Multi-Agent Debate

Five independent AI "experts" (running different Ollama models) each analyze your prompt independently — gathering web context, recalling past strategies from a local vector database, and drafting their own answers. A designated **Judge model** then reads all five responses and synthesizes a single **Consensus Answer**, picking the best reasoning from each expert.

> **Think of it as:** A panel of five senior engineers debating a design decision, with a CTO making the final call.

---

### 🤖 The Autonomous SRE — Self-Healing Terminal Agent

Genesis features a **ReAct (Reason → Act → Observe)** execution loop. Instead of blindly running a list of commands and crashing at the first error, the agent:

1.  **Thinks** — Analyzes the objective and decides the next command.
2.  **Acts** — Executes a single bash command on your terminal.
3.  **Observes** — Reads the output. If it failed, it diagnoses the error and writes a corrective command.

The agent also has access to a **Web Search tool**, so if it encounters an unknown command or syntax, it can search the internet for the correct approach before acting.

> **Think of it as:** An SRE on-call who reads the error logs, Googles the fix, and patches the system — all autonomously.

---

### 🏗️ The Codebase Architect — Local Directory RAG

Point Genesis at any local project directory (e.g., your Terraform infrastructure repo), and it will:

1.  **Ingest** — Recursively scan all source files (`.py`, `.tf`, `.tfvars`, `.yaml`, `.json`, `.sh`, `.md`, etc.).
2.  **Chunk & Embed** — Split files into semantic chunks and store them in a local **ChromaDB** vector database.
3.  **Retrieve & Answer** — When you ask a question, it performs a semantic search against your codebase and feeds the relevant code directly to the LLM — completely offline.

> **Think of it as:** A Staff DevOps Architect who has read every single file in your repo and can answer deep architectural questions instantly.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🏛️ **Multi-Agent Debate** | 5 independent LLM experts + 1 Judge synthesizer |
| 🔬 **Deep Research Mode** | Multi-pass web-grounded research with structured reports |
| 🛡️ **Security Audit Mode** | Generates multi-step SecOps execution plans |
| 🤖 **Self-Healing ReAct Agent** | Autonomous terminal execution with error recovery |
| 🌐 **Dynamic Web Search** | Agent can search the internet mid-execution |
| 🏗️ **Codebase RAG** | Ingest local directories for architecture Q&A |
| 📄 **PDF RAG** | Upload PDFs and query their contents |
| 🧠 **Shared Brain (ChromaDB)** | Persistent vector memory across sessions |
| 🎨 **Gemini-Themed UI** | Dark mode, Google Sans typography, Streamlit |
| 💻 **100% Local & Private** | No API keys, no cloud, no telemetry |

---

## 📋 Prerequisites

Before you begin, ensure you have the following:

-   **Python 3.9+** — [Download](https://www.python.org/downloads/)
-   **Ollama** — Local LLM runtime. [Install Ollama](https://ollama.com/download)
-   **macOS or Linux** — Terminal execution features are optimized for Unix-based systems.
-   **16 GB RAM recommended** — For running multiple 7B-14B parameter models.

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sharansutrapu/Genesis.git
cd Genesis
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Pull the Required Ollama Models

Genesis uses a council of models. Pull the ones you want to use:

```bash
# Recommended Council (edit COUNCIL_MODELS in hive_orchestrator.py to customize)
ollama pull dolphin-llama3
ollama pull qwen2.5-coder:7b
ollama pull mistral
ollama pull phi3
ollama pull llama3.2
```

### 5. Launch Genesis

```bash
streamlit run app.py
```

Genesis will open in your browser at `http://localhost:8501`.

---

## ⚙️ How It Works — Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     STREAMLIT UI                        │
│  (Chat Interface, Mode Selector, Sidebar Controls)      │
└──────────────┬──────────────────────────────┬───────────┘
               │                              │
               ▼                              ▼
┌──────────────────────┐        ┌──────────────────────────┐
│   HIVE ORCHESTRATOR  │        │    SHARED BRAIN          │
│                      │        │    (ChromaDB)            │
│  • Intent Router     │◄──────►│  • Strategy Recall       │
│  • Council Debate    │        │  • Codebase RAG          │
│  • Deep Research     │        │  • Reflection Storage    │
│  • SecOps Planner    │        └──────────────────────────┘
│  • ReAct Agent       │
│  • Exec Summarizer   │        ┌──────────────────────────┐
│                      │───────►│    OLLAMA (Local LLMs)   │
└──────────┬───────────┘        │  • dolphin-llama3        │
           │                    │  • qwen2.5-coder         │
           ▼                    │  • mistral, phi3, etc.   │
┌──────────────────────┐        └──────────────────────────┘
│   EXECUTION ENGINE   │
│                      │        ┌──────────────────────────┐
│  • subprocess.run()  │───────►│    WEB SEARCH (DuckDuckGo│
│  • ReAct Loop        │        │    via ddgs library)     │
│  • Web Search Tool   │        └──────────────────────────┘
└──────────────────────┘
```

### Data Flow

1.  **User submits a prompt** via the Streamlit chat input.
2.  **Intent Router** classifies the prompt as `CASUAL`, `COMMAND`, or `TASK`.
3.  **Mode Override** — If the user selected Security Audit or Codebase Architect, the intent router is bypassed entirely.
4.  **Context Gathering** — The orchestrator searches the web (DuckDuckGo), recalls past strategies from ChromaDB, and optionally retrieves codebase/PDF chunks.
5.  **Model Execution** — Depending on the mode, one or more Ollama models process the prompt.
6.  **Response Rendering** — The final consensus is rendered in the Gemini-themed UI.

---

## 📂 Project Structure

```
Genesis/
├── app.py                    # Streamlit UI & execution engine
├── hive_orchestrator.py      # Multi-agent orchestration core
├── cleanup.py                # Data sanitization script
├── requirements.txt          # Python dependencies
├── setup_hive.sh             # Initial setup helper
├── memory/
│   ├── shared_brain.py       # ChromaDB vector store interface
│   ├── chromadb_data/        # Persistent vector database (auto-created)
│   └── chat_sessions.json    # Chat history (auto-created)
└── tools/
    └── web_search.py         # DuckDuckGo web search utility
```

---

## 🧹 Cleanup (Before Sharing)

To remove all personal data, chat history, and test artifacts:

```bash
python cleanup.py
```

---

## 🛣️ Roadmap

- [ ] Multi-modal support (image analysis)
- [ ] Plugin system for custom tools
- [ ] Docker containerization
- [ ] Remote Ollama server support
- [ ] Export reports to PDF/Markdown

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 👨‍💻 About the Author

**Sharan Kumar Reddy Sutrapu**

Cloud Infrastructure & DevOps Engineer with a passion for AI-augmented automation and multi-agent systems.

| Platform | Link |
|---|---|
| 🌐 Website | [sharansutrapu.com](https://sharansutrapu.com/) |
| 💼 LinkedIn | [Sharan Kumar Reddy Sutrapu](https://www.linkedin.com/in/sharan-kumar-reddy-sutrapu-34b50519b/) |
| 💻 GitHub | [@sharansutrapu](https://github.com/sharansutrapu) |
| 📝 Medium | [@sharansutrapu](https://medium.com/@sharansutrapu) |
| 📸 Instagram | [@sharansutrapu](https://www.instagram.com/sharansutrapu/) |
| 📘 Facebook | [Sharan Kumar Reddy Sutrapu](https://www.facebook.com/sutrapusharan) |

---

<p align="center">
  Built with ❤️ on Apple Silicon — Powered by Ollama & Streamlit
</p>
