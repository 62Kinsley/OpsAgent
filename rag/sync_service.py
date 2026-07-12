from rag.vector_store import VectorStore

def main():
    vs = VectorStore()
    vs.load_split_store()
    print("Knowledge sync completed.")

if __name__ == "__main__":
    main()