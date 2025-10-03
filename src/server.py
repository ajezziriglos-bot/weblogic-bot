from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="KB RAG Bot")

class Ask(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"ok": True}

# Import diferido del RAG para no romper el arranque ni ocultar /ask
_import_err = None
_ask_rag = None
try:
    from .rag import ask_rag as _ask_rag
except Exception as e:
    _import_err = e

@app.post("/ask")
def ask(a: Ask):
    if _import_err is not None:
        return {
            "error": "RAG import failed",
            "detail": str(_import_err),
            "hint": "Revisá src/rag.py / embeddings / chroma / ollama."
        }
    return {"answer": _ask_rag(a.question)}
