import os
import sqlite3
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_unstructured import UnstructuredLoader
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from os import getenv

# Zotero DB und Speicherpfad anpassen
ZOTERO_DB_PATH = os.path.expanduser(r'C:\Users\ehler\Zotero\zotero.sqlite')
ZOTERO_STORAGE_FOLDER = r'C:\Users\ehler\Zotero\storage'
LOCAL_PDF_FOLDER = r'C:\Pfad\zu\deinen\lokalen\PDFs'  # Pfad zu deinen lokalen PDFs

load_dotenv()
embed_model = OllamaEmbeddings(model=getenv("EMBEDDING_MODEL"))

# Funktion, um Zotero-PDFs zu extrahieren
def get_zotero_pdfs():
    conn = sqlite3.connect(ZOTERO_DB_PATH)
    cursor = conn.cursor()

    # Hole die Dateipfade und ihre itemIDs für PDF-Dateien
    cursor.execute("SELECT itemID, path FROM itemAttachments WHERE contentType='application/pdf';")
    attachments = cursor.fetchall()

    # Erstelle eine Liste von PDF-Dateien mit vollständigen Pfaden
    pdfs = []
    for attachment in attachments:
        item_id, file_path = attachment

        # Überprüfen, ob der Pfad mit 'storage:' beginnt
        if file_path.startswith("storage:"):
            relative_path = file_path.replace("storage:", "")

            # Durchsuche alle Unterordner von Zotero 'storage'
            for root, dirs, files in os.walk(ZOTERO_STORAGE_FOLDER):
                if relative_path in files:
                    full_file_path = os.path.join(root, relative_path)
                    if os.path.exists(full_file_path):
                        pdfs.append(full_file_path)
                    else:
                        print(f"Datei nicht gefunden: {full_file_path}")
                    break  # Wenn die Datei gefunden wurde, beende die Schleife

    conn.close()
    return pdfs

# Funktion, um lokale PDFs zu extrahieren
def get_local_pdfs():
    pdfs = []
    # Durchsuche den angegebenen Ordner nach PDFs
    for root, dirs, files in os.walk(LOCAL_PDF_FOLDER):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_file_path = os.path.join(root, file)
                pdfs.append(full_file_path)
    return pdfs

# Load and chunk the file
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

# Lade und verarbeite Zotero- und lokale PDFs
def load_zotero_and_local_data_and_save_to_vectorstore():
    # Hole Zotero-PDFs und lokale PDFs
    zotero_pdfs = get_zotero_pdfs()
    local_pdfs = get_local_pdfs()

    # Kombiniere alle PDFs
    all_pdfs = zotero_pdfs + local_pdfs

    # Lade und chunk die PDFs
    all_documents = []
    for pdf in all_pdfs:
        print(f"Loading and chunking file: {pdf}")
        docs = load_and_chunk(pdf)
        if docs:
            all_documents.extend(docs)

    # Wenn keine PDFs gefunden wurden
    if not all_documents:
        print("Keine PDF-Dokumente zum Laden gefunden.")
        return

    # Erstelle und speichere den VectorStore
    save_to_vectorstore(all_documents)
    print("PDFs wurden erfolgreich in den Vectorstore geladen.")

# Hauptteil des Programms
if __name__ == "__main__":
    print("Loading Zotero and local PDFs and saving to vectorstore...")
    load_zotero_and_local_data_and_save_to_vectorstore()
    print("Done!")
