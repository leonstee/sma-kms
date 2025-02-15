import os
from langchain_ollama import OllamaEmbeddings
from langchain_unstructured import UnstructuredLoader
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv

from config import (
    ZOTERO_STORAGE_FOLDER,
    LOCAL_PDF_FOLDER,
    OBSIDIAN_MD_FOLDER,
    EMBEDDING_MODEL,
    QDRANT_URL,
    QDRANT_COLLECTION, OLLAMA_HOST
)


load_dotenv()  # Lädt Umgebungsvariablen aus einer .env-Datei
embed_model = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_HOST)  # Initialisiert das Embedding-Modell

# Funktion, um Zotero-PDFs zu extrahieren
def get_files_by_extension(folder_path, extension):
    """
    Durchsucht einen Ordner rekursiv nach Dateien mit einer bestimmten Erweiterung.

    :param folder_path: Pfad zum Verzeichnis, das durchsucht werden soll
    :param extension: Dateierweiterung (z. B. ".pdf", ".md")
    :return: Liste der gefundenen Dateien mit vollständigem Pfad
    """
    files = []
    for root, _, file_names in os.walk(folder_path):
        for file in file_names:
            if file.lower().endswith(extension.lower()):
                files.append(os.path.join(root, file))
    return files

# Spezifische Funktionen mit vordefinierten Pfaden und Dateitypen
def get_zotero_pdfs():
    return get_files_by_extension(ZOTERO_STORAGE_FOLDER, ".pdf")

def get_local_pdfs():
    return get_files_by_extension(LOCAL_PDF_FOLDER, ".pdf")

def get_obsidian_md_files():
    return get_files_by_extension(OBSIDIAN_MD_FOLDER, ".md")

# Lade und chunk die Datei
def load_and_chunk(file_path):
    try:
        unstructured_loader = UnstructuredLoader(
            file_path=file_path,  # Pfad zur Datei
            chunking_strategy="by_title",  # Chunking-Strategie (nach Titel)
            max_characters=1200,  # Maximale Anzahl von Zeichen pro Chunk
            new_after_n_chars=500,  # Neuer Chunk nach 500 Zeichen
            overlap=120,  # Überlappung von 120 Zeichen zwischen Chunks
            include_orig_elements=False,  # Die Originalelemente werden nicht mit einbezogen
        )
        unstructured_docs = unstructured_loader.load()  # Lade und chunk die Datei
        return unstructured_docs  # Rückgabe der gechunkten Dokumente
    except Exception as e:
        print(f"Error loading and chunking file: {e}")  # Fehlerbehandlung
        return None


def save_to_vectorstore(docs, file_path=None):  # file_path als optionales Argument hinzufügen
    try:
        url = QDRANT_URL
        print(f"Saving to vectorstore: {url}")

        # Dokumente mit einer Priorität versehen und ggf. Dateipfad in Metadaten speichern
        prioritized_docs = []
        for doc in docs:
            if 'zotero' in doc.metadata.get('source', '').lower():
                doc.metadata['priority'] = 1  # Höchste Priorität für Zotero
            elif 'obsidian' in doc.metadata.get('source', '').lower():
                doc.metadata['priority'] = 2  # Mittlere Priorität für Obsidian
            else:
                doc.metadata['priority'] = 3  # Niedrigere Priorität für lokale PDFs

            # Falls `file_path` vorhanden ist, in den Metadaten speichern
            if file_path:
                doc.metadata["file_path"] = file_path

            prioritized_docs.append(doc)

        # Vector Store mit den priorisierten Dokumenten erstellen
        unstructured_chunk_vectorstore = QdrantVectorStore.from_documents(
            prioritized_docs,
            embed_model,
            url=url,
            prefer_grpc=False,
            collection_name=QDRANT_COLLECTION,
        )
    except Exception as e:
        print(f"Error saving to vectorstore: {e}")


# Lade und verarbeite Zotero-, Obsidian und lokale PDFs
def load_all_data_and_save_to_vectorstore():
    # Hole Zotero-PDFs und lokale PDFs
    zotero_pdfs = get_zotero_pdfs()
    local_pdfs = get_local_pdfs()
    obsidian_md_files = get_obsidian_md_files()

    # Kombiniere alle PDFs
    all_files = zotero_pdfs + local_pdfs + obsidian_md_files

    # Lade und chunk die Dateien
    all_documents = []
    for file in all_files:
        print(f"Loading and chunking file: {file}")  # Zeige an, welche Datei geladen wird
        docs = load_and_chunk(file)
        if docs:  # Wenn Dokumente erfolgreich gechunked wurden
            all_documents.extend(docs)

    # Wenn keine Dokumente gefunden wurden
    if not all_documents:
        print("Keine Dokumente zum Laden gefunden.")
        return
    # Erstelle und speichere den VectorStore
    save_to_vectorstore(all_documents)
    print("Dokumente wurden erfolgreich in den Vectorstore geladen.")

# Hauptteil des Programms
if __name__ == "__main__":
    print("Loading Zotero and local PDFs and saving to vectorstore...")
    load_all_data_and_save_to_vectorstore()  # Lade alle Daten und speichere sie im Vector Store
    print("Done!")
