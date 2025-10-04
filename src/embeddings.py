import os
import httpx
import time  # <- necesario para el throttle opcional
from typing import List
from .config import settings

BACKEND = os.getenv("EMBED_BACKEND", "OLLAMA").upper()

if BACKEND == "ST":
    from sentence_transformers import SentenceTransformer
    _st_model_name = os.getenv("ST_MODEL", settings.ST_MODEL)
    _st_model = SentenceTransformer(_st_model_name)

    class OllamaEmbeddings:
        """Conservamos el nombre por compatibilidad."""
        def __init__(self, model: str = settings.EMBED_MODEL, base_url: str = "http://localhost:11434"):
            pass
        def embed(self, texts: List[str]) -> List[List[float]]:
            # normalize_embeddings=True mejora similitud coseno
            return _st_model.encode(texts, normalize_embeddings=True).tolist()

else:
    # Ollama backend (usa /api/embeddings)
    class OllamaEmbeddings:
        def __init__(self, model: str = settings.EMBED_MODEL, base_url: str = "http://localhost:11434"):
            self.model = model
            self.base_url = base_url
        def embed(self, texts: List[str]) -> List[List[float]]:
            vecs: List[List[float]] = []
            with httpx.Client(timeout=60) as client:
                for t in texts:
                    r = client.post(
                        f"{self.base_url}/api/embeddings",
                        json={"model": self.model, "prompt": t}
                    )
                    if r.status_code == 404 and "not found" in r.text.lower():
                        raise RuntimeError(
                            f"Embeddings model '{self.model}' no está instalado en Ollama. "
                            f"Ejecutá: ollama pull {self.model}"
                        )
                    r.raise_for_status()
                    vecs.append(r.json()["embedding"])
                    # throttle opcional ultra pequeño para WSL
                    time.sleep(float(os.getenv("EMBED_THROTTLE_SEC", "0.0")))
            return vecs
