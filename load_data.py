from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_unstructured import UnstructuredLoader
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from os import getenv

load_dotenv()

embed_model = OllamaEmbeddings(model=getenv("EMBEDDING_MODEL"))

# Load the file and chunk it
def load_and_chunk(file_path):
    try:
        unstructured_loader = UnstructuredLoader(
            file_path=file_path,
            chunking_strategy="by_title",
            max_characters=1200,
            new_after_n_chars=500,
            overlap=120,
            include_orig_elements=False,
        )
        unstructured_docs = unstructured_loader.load()
        return unstructured_docs
    except Exception as e:
        print(f"Error loading and chunking file: {e}")
        return None


# Save chunked file to Vector Store
def save_to_vectorstore(docs):
    try:
        url = getenv("QDRANT_URL")
        unstructured_chunk_vectorstore = QdrantVectorStore.from_documents(
            docs,
            embed_model,
            url=url,
            prefer_grpc=False,
            collection_name=getenv("QDRANT_COLLECTION"),
        )
    except Exception as e:
        print(f"Error saving to vectorstore: {e}")


if __name__ == "__main__":
    file_path = "IT_Grundschutz_Kompendium_Edition2023_17-60.pdf"
    print(f"Loading and chunking file: {file_path}")
    docs = load_and_chunk(file_path)
    print(f"Saving to vectorstore...")
    save_to_vectorstore(docs)
    print("Done!")

