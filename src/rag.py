# src/rag.py
# -*- coding: utf-8 -*-
from typing import List
import httpx

from .config import settings
from .embeddings import OllamaEmbeddings
from .vectorstore import query as vs_query

SYSTEM_RAG = """Eres un asistente técnico L1/L2 (p. ej., infraestructura Oracle WebLogic).
Respondes SOLO con información basada en el contexto provisto (fragmentos recuperados).
Si falta información para responder con seguridad, dilo claramente y sugiere qué documento o dato cargar.
Responde conciso y con pasos accionables cuando corresponda (comandos, WLST, AdminServer, etc.).
No inventes datos que no estén en el contexto. Formato preferido: viñetas y/o pasos.
"""

USER_RAG_TEMPLATE = """Pregunta del usuario:
{question}

Contexto recuperado (fragmentos relevantes):
{context}

Instrucciones:
- Usa estrictamente la información del contexto.
- Si el contexto es insuficiente o ambiguo, dilo.
- Da comandos/pasos concretos cuando aplique.
"""

def _format_context(res) -> str:
    if not res or not res.get("documents"):
        return "SIN CONTEXTO"
    docs_all = res.get("documents") or []
    metas_all = res.get("metadatas") or []
    if not docs_all or not docs_all[0]:
        return "SIN CONTEXTO"
    docs = docs_all[0]
    metas = metas_all[0] if metas_all else [{}] * len(docs)
    lines: List[str] = []
    for d, m in zip(docs, metas):
        src = m.get("source", "desconocido")
        idx = m.get("chunk_index", "?")
        lines.append(f"[{src} #{idx}] {d}")
    return "\n\n".join(lines) if lines else "SIN CONTEXTO"

def _truncate(text: str, max_chars: int = 8000) -> str:
    return text if len(text) <= max_chars else text[:max_chars] + "\n...[contexto truncado]"

def _llm_generate(system: str, user: str) -> str:
    prompt = f"<<SYS>>\n{system}\n<</SYS>>\n\n{user}\n"
    with httpx.Client(timeout=600) as client:
        r = client.post(
            "http://localhost:11434/api/generate",
            json={
                "model": settings.LLM_MODEL,
                "prompt": prompt,
                "options": {"temperature": settings.TEMPERATURE, "num_predict": settings.MAX_TOKENS},
                "stream": False,
            },
        )
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(f"Ollama generate error: {data['error']}")
        if "response" not in data:
            raise RuntimeError(f"Ollama generate unexpected payload: {data}")
        return data["response"]

def ask_rag(question: str) -> str:
    emb = OllamaEmbeddings()
    qv = emb.embed([question])[0]
    res = vs_query(qv, settings.TOP_K)
    context = _truncate(_format_context(res), max_chars=8000)
    user_prompt = USER_RAG_TEMPLATE.format(question=question, context=context)
    answer = _llm_generate(SYSTEM_RAG, user_prompt)
    return answer.strip()

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]).strip() or "como reinicio un weblogic"
    try:
        print(ask_rag(q))
    except Exception as e:
        print("Error en ask_rag:", e)
