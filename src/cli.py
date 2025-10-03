import sys
from .rag import ask_rag

def main():
    q = " ".join(sys.argv[1:]).strip()
    if not q:
        print("Uso: python -m src.cli \"tu pregunta\"")
        sys.exit(1)
    print(ask_rag(q))

if __name__ == "__main__":
    main()
