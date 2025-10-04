from __future__ import annotations
from pathlib import Path
from typing import ClassVar
from pydantic_settings import BaseSettings  # <- OJO: v2 usa pydantic_settings

class Settings(BaseSettings):
    # -------- Fields (todos tipados) --------

    EMBED_BACKEND: str = "ST"  # "ST" o "OLLAMA"
    ST_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    LLM_MODEL: str = "llama3.2:3b"
    EMBED_MODEL: str = "nomic-embed-text"

    KB_DIR: str = "./data/kb"
    CHROMA_DIR: str = "./data/chroma"

    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    TOP_K: int = 3
    MAX_TOKENS: int = 600
    TEMPERATURE: float = 0.1

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # -------- Constantes (NO fields) --------
    APP_NAME: ClassVar[str] = "KB RAG Bot"

    class Config:
        env_file = ".env"

settings = Settings()

# Crear carpetas si no existen
Path(settings.KB_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.CHROMA_DIR).mkdir(parents=True, exist_ok=True)
