# 🧬 PROJECT GENESIS: Hive Mind Architecture

**Objective:** Build a Multi-Agent consensus system, an Autonomous SRE, and a Codebase Architect using local Small Language Models (SLMs) orchestrated via Ollama.
**Constraint:** 100% Local Execution, Zero Cloud APIs.

## 1. The True Council (Debate Architecture)
Genesis abandons linear generation for a parallel consensus model.

* **Phase 1 (Independent Drafting):** Up to 5 models (e.g., qwen2.5-coder, deepseek-r1, phi4) receive the exact same prompt and context. They operate sequentially in code to prevent OOM errors, but act logically as independent, parallel experts. They do not see each other's answers.
* **Phase 2 (Judgement):** A designated Lead Model (e.g., dolphin-llama3) receives all 5 independent drafts, synthesizes the strongest technical arguments, and outputs a single definitive Consensus.

## 2. The Autonomous SRE (ReAct Execution Engine)
For infrastructure tasks, Genesis shifts from "chat" to "execution" using a ReAct (Reason + Act + Observe) loop via Python's `subprocess`.
* **Dynamic Tooling:** The model selects between `COMMAND` (execute in terminal) and `SEARCH` (query DuckDuckGo).
* **Self-Healing:** If a bash command returns an exit code `> 0`, the engine captures `stderr`, feeds the stack trace back to the LLM's context, and forces it to generate a patched command.

## 3. The Codebase Architect (Local Directory RAG)
Genesis features a custom ingestion engine using ChromaDB.
* **Ingestion:** Scans local project directories (`.tf`, `.py`, `.yaml`, `.tfvars`, etc.), chunks the codebase, and embeds it into a local vector store.
* **Retrieval:** Bypasses web searches to inject highly relevant proprietary code directly into the LLM's optic nerve, allowing for deep architectural audits (e.g., "Find open security group ingress rules in this Terraform module").

## 🛠️ Tech Stack
* **Orchestration:** Python 3.9+
* **UI:** Streamlit (Custom Gemini-Themed UI)
* **Inference:** Ollama Python Client
* **Memory/Vector Store:** ChromaDB
* **Web Search:** DuckDuckGo Search (`ddgs`)