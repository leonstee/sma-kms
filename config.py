import os
from dotenv import load_dotenv

# .env-Datei laden, falls vorhanden
load_dotenv()


OLLAMA_HOST = "http://host.docker.internal:11434" # bei Nutzung in Docker

# OLLAMA_HOST= os.getenv("OLLAMA_HOST", "http://localhost:11434") # bei lokaler Entwicklung
LM_MODEL = os.getenv("LM_Model", "qwen2.5:7b-instruct")



# Zotero-Pfade
ZOTERO_STORAGE_FOLDER = "/zotero" # bei Nutzung in Docker
#ZOTERO_STORAGE_FOLDER = os.getenv("ZOTERO_STORAGE_FOLDER") # bei lokaler Entwicklung


# Lokale Ordner
LOCAL_PDF_FOLDER = "/pdfs" # bei Nutzung in Docker
#LOCAL_PDF_FOLDER = os.getenv("LOCAL_PDF_FOLDER") # bei lokaler Entwicklung
OBSIDIAN_MD_FOLDER ="/obsidian" # bei Nutzung in Docker
#OBSIDIAN_MD_FOLDER = os.getenv("OBSIDIAN_MD_FOLDER") # bei lokaler Entwicklung

# Embedding- und Vector Store-Konfiguration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3")

QDRANT_URL = "http://db:6333" # bei Nutzung in Docker
#QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333") # bei lokaler Entwicklung

QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "sma-kms")

# Verzeichnisse für die Überwachung
WATCHED_FOLDERS = [
    ZOTERO_STORAGE_FOLDER,
    LOCAL_PDF_FOLDER,
    OBSIDIAN_MD_FOLDER
]
