# src/ingest.py
# -*- coding: utf-8 -*-
"""
Ingesta de KB a Chroma con embeddings locales.

- Archivos soportados: .md, .txt, .pdf (PDF requiere pypdf)
- Usa OllamaEmbeddings por defecto (Ollama /api/embeddings).
- Si exportás EMBED_BACKEND=ST, usa sentence-transformers local (más liviano).
- Procesa en batches para no saturar memoria/CPU.

Requiere:
  - src/config.py        -> settings (KB_DIR, CHUNK_SIZE, etc.)
  - src/embeddings.py    -> OllamaEmbeddings (maneja EMBED_BACKEND/ ST)
  - src/vectorstore.py   -> clear_collection, add_docs
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any, Iterable
import os
import re
import time

from .config import settings
from .embeddings import OllamaEmbeddings
from .vectorstore import clear_collection, add_docs


# ------------------------------- Utils FS -------------------------------

SUPPORTED_EXTS = (".md", ".txt", ".pdf")


def iter_kb_files(kb_dir: Path) -> List[Path]:
    """Lista recursivamente archivos soportados en kb_dir."""
    files: List[Path] = []
    for ext in ("*.md", "*.txt", "*.pdf"):
        files.extend(kb_dir.rglob(ext))
    # orden estable
    files = sorted([p for p in files if p.is_file()])
    return files


# ------------------------------ Lectura --------------------------------

def read_text(path: Path) -> str:
    """Lee texto de .md/.txt o extrae de .pdf (si hay pypdf)."""
    suf = path.suffix.lower()
    try:
        if suf in {".md", ".txt"}:
            return path.read_text(encoding="utf-8", errors="ignore")
        if suf == ".pdf":
            try:
                from pypdf import PdfReader  # type: ignore
            except Exception as e:
                print(f"[WARN] PDF omitido (falta pypdf) -> {path.name}: {e}")
                return ""
            reader = PdfReader(str(path))
            pages = []
            for i, pg in enumerate(reader.pages):
                try:
                    pages.append(pg.extract_text() or "")
                except Exception as pe:
                    print(f"[WARN] No se pudo extraer texto de página {i} en {path.name}: {pe}")
            return "\n".join(pages)
    except Exception as e:
        print(f"[WARN] No se pudo leer {path.name}: {e}")
    return ""


# ------------------------------ Chunking -------------------------------

def chunk_text(text: str, size: int, overlap: int) -> List[str]:
    """Divide texto en chunks solapados size/overlap."""
    # Limpieza simple de espacios
    text = re.sub(r"[ \t]+\n", "\n", text).strip()
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    L = len(text)
    while start < L:
        end = min(L, start + size)
        chunks.append(text[start:end])
        if end >= L:
            break
        start = max(0, end - overlap)
    return chunks


# ----------------------------- Embeddings ------------------------------

def batched(iterable: List[str], n: int) -> Iterable[List[str]]:
    """Yield listas en lotes de tamaño n."""
    for i in range(0, len(iterable), n):
        yield iterable[i : i + n]


def embed_all(documents: List[str], batch_size: int = 128, throttle_sec: float = 0.0) -> List[List[float]]:
    """
    Genera embeddings en batches.
    - Si EMBED_BACKEND=ST, usa sentence-transformers (rápido y liviano).
    - Si no, usa Ollama /api/embeddings (asegurate de tener 'nomic-embed-text').
    """
    emb = OllamaEmbeddings()  # esta clase respeta EMBED_BACKEND en embeddings.py
    out: List[List[float]] = []
    total = len(documents)
    done = 0
    for batch in batched(documents, batch_size):
        vecs = emb.embed(batch)
        out.extend(vecs)
        done += len(batch)
        print(f"  - Embeddings: {done}/{total}")
        if throttle_sec > 0:
            time.sleep(throttle_sec)
    return out


# ----------------------------- Pipeline --------------------------------

def main():
    # Sugerencias para no saturar BLAS en WSL:
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

    kb_dir = Path(settings.KB_DIR)
    kb_dir.mkdir(parents=True, exist_ok=True)

    print(f"KB_DIR: {kb_dir.resolve()}")
    files = iter_kb_files(kb_dir)
    print(f"Archivos encontrados ({len(files)}): {[str(p) for p in files]}")

    # Construir dataset de chunks
    ids: List[str] = []
    docs: List[str] = []
    metas: List[Dict[str, Any]] = []

    total_files = 0
    skipped_empty = 0

    for path in files:
        if path.suffix.lower() not in SUPPORTED_EXTS:
            continue
        total_files += 1
        txt = read_text(path)
        chs = chunk_text(txt, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        if not chs:
            skipped_empty += 1
            print(f"[WARN] Sin texto/chunks -> {path.name}")
            continue
        for i, ch in enumerate(chs):
            ids.append(f"{path.name}-{i}")
            docs.append(ch)
            metas.append({"source": str(path), "chunk_index": i})

    print(f"Total archivos procesados: {total_files} | vacíos/omitidos: {skipped_empty}")
    print(f"Total chunks: {len(docs)}")

    if not docs:
        print("Nada para indexar. ¿Tenés archivos .md/.txt/.pdf con texto en KB_DIR?")
        return

    # Embeddings (elige backend por EMBED_BACKEND; default = OLLAMA)
    backend = os.getenv("EMBED_BACKEND", "OLLAMA").upper()
    print(f"Backend de embeddings: {backend}")
    if backend == "OLLAMA":
        print("Asegurate de tener Ollama corriendo y el modelo de embeddings instalado:")
        print("  - ollama serve")
        print("  - ollama pull nomic-embed-text")

    # Batch/respiro: ajustables por env
    batch_size = int(os.getenv("INGEST_BATCH", "128"))
    throttle = float(os.getenv("INGEST_THROTTLE_SEC", "0.0"))

    print(f"Generando embeddings en batches de {batch_size} (throttle={throttle}s)…")
    vecs = embed_all(docs, batch_size=batch_size, throttle_sec=throttle)

    print("Persistiendo en Chroma (limpia y re-crea la colección)…")
    clear_collection()
    add_docs(ids, docs, metas, vecs)
    print("Ingesta completa y persistida en Chroma.")


if __name__ == "__main__":
    main()
