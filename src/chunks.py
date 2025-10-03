from typing import List, Tuple
from pypdf import PdfReader
from pathlib import Path
from markdown_it import MarkdownIt

def read_text_file(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")

def read_pdf_file(p: Path) -> str:
    reader = PdfReader(str(p))
    texts = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        texts.append(txt)
    return "\n".join(texts)

def read_md_file(p: Path) -> str:
    # Render markdown to plain-ish text (strip formatting)
    md = MarkdownIt()
    tokens = md.parse(p.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join([t.content for t in tokens if t.content])

def load_file_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return read_pdf_file(path)
    if path.suffix.lower() == ".md":
        return read_md_file(path)
    return read_text_file(path)

def split_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        chunks.append(text[start:end])
        start = end - overlap
        if start < 0: start = 0
        if start >= length: break
    return chunks

def iter_kb_files(kb_dir: str) -> List[Path]:
    paths = []
    for ext in ("*.txt","*.md","*.pdf"):
        paths.extend(Path(kb_dir).glob(ext))
    return paths
