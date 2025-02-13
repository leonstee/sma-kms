import os
from dotenv import load_dotenv

# .env-Datei laden, falls vorhanden
load_dotenv()

# Zotero-Pfade
ZOTERO_DB_PATH = os.path.expanduser(r'C:\Users\ehler\Zotero\zotero.sqlite')
ZOTERO_STORAGE_FOLDER = os.path.expanduser(r'C:\Users\ehler\Zotero\storage')

# Lokale Ordner
LOCAL_PDF_FOLDER = os.path.expanduser(r'C:\Users\ehler\PycharmProjects\sma-kms')
OBSIDIAN_MD_FOLDER = os.path.expanduser(r'C:\Users\ehler\Documents\Hochschule Mannheim\Semester3\SMA\SMA')

# Embedding- und Vector Store-Konfiguration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION")

# Verzeichnisse für die Überwachung
WATCHED_FOLDERS = [
    ZOTERO_STORAGE_FOLDER,
    LOCAL_PDF_FOLDER,
    OBSIDIAN_MD_FOLDER
]
