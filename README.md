WebLogic KB RAG Bot (L1/L2)

A lightweight, local RAG (Retrieval-Augmented Generation) assistant that answers L1/L2 support questions using your own knowledge base (Markdown/TXT/PDF). It runs fully on your machine, indexes docs with Chroma, generates answers with Ollama (or a local sentence-transformers model for embeddings), and exposes a simple FastAPI endpoint you can call from scripts, tools, or a chat UI.

Why this project?

Own your data: everything runs locally—no cloud calls.

Operational answers: optimized for infrastructure runbooks (e.g., Oracle WebLogic), with step-by-step guidance and command snippets.

Practical dev setup: Python + VS Code + virtualenv; minimal dependencies; works well on WSL.

Features

🔎 RAG over your KB (Markdown, TXT, PDF)

🧠 Embeddings via Ollama (nomic-embed-text) or sentence-transformers (fast on WSL)

🗃️ Persistent vector store with Chroma

🤖 LLM via Ollama (default llama3.2:3b for low RAM; upgrade anytime)

🌐 FastAPI endpoints: health check and /ask

🧱 Config via .env (models, chunk size, top-k, paths)

Tech Stack

Python, FastAPI, Uvicorn

ChromaDB (persistent client)

Ollama (LLM + embeddings) or sentence-transformers (embeddings)

pydantic-settings for config

Quickstart
python -m venv .venv
source .venv/bin/activate
pip install -U pip -r requirements.txt
cp .env.example .env   # edit if needed

# Put your docs in ./data/kb (md/txt/pdf)
python -m src.ingest

# Run API
export EMBED_BACKEND=ST; export ST_MODEL=sentence-transformers/all-MiniLM-L6-v2; PYTHONPATH=. uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload

Test it

curl -s http://localhost:8000/health

curl -s -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  --data '{"question":"como reinicio un weblogic"}' | jq
  

Configuration

.env / src/config.py: model names, chunking, top-k, paths.

WSL tip: for low-RAM environments, set EMBED_BACKEND=ST and LLM_MODEL=llama3.2:3b.

