weblogic-bot/
├─ .env.example
├─ README.md
├─ requirements.txt
├─ data/
│  ├─ kb/             # Tus docs: .md/.txt/.pdf (p.ej. weblogic_faq.md)
│  └─ chroma/         # Carpeta de la base vectorial (se crea sola)
└─ src/
   ├─ config.py
   ├─ embeddings.py
   ├─ vectorstore.py
   ├─ chunks.py
   ├─ ingest.py
   ├─ prompts.py
   ├─ rag.py
   ├─ server.py       # FastAPI /ask
   ├─ cli.py          # Línea de comando: python -m src.cli "pregunta"
   └─ tools.py        # (Fase 2) acciones y loop de herramientas