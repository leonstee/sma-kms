import os
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from dotenv import load_dotenv
from load_data import load_and_chunk, save_to_vectorstore
from config import QDRANT_URL, QDRANT_COLLECTION, WATCHED_FOLDERS

load_dotenv()

# Verbindung zur Vektordatenbank mit Werten aus config.py
client = QdrantClient(url=QDRANT_URL)
collection_name = QDRANT_COLLECTION


class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".pdf") or event.src_path.endswith(".md"):
            print(f"Geänderte Datei erkannt: {event.src_path}")
            self.process_file(event.src_path, is_update=True)

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".pdf") or event.src_path.endswith(".md"):
            print(f"Neue Datei erkannt: {event.src_path}")
            self.process_file(event.src_path, is_update=False)

    def on_deleted(self, event):
        if event.is_directory:
            return
        print(f"Datei gelöscht: {event.src_path}")
        self.delete_all_vectors_with_filename(event.src_path)

    def process_file(self, file_path, is_update=False):
        # Lade und chunk die Datei

        if is_update:
            print(f"lösche alte Vektorne vor dem Neuspeichern für: {file_path}")
            self.delete_all_vectors_with_filename(file_path)


        docs = load_and_chunk(file_path)
        if docs:
            # Speichere die chunked-Daten in der Vektordatenbank
            save_to_vectorstore(docs, file_path)  # Dateipfad weitergeben
            print(f"Datei verarbeitet und gespeichert: {file_path}")

    def delete_all_vectors_with_filename(self, filepath: str):
        """
        Löscht alle Vektoren mit dem angegebenen Dateinamen aus dem Vektorstore.

        :param filepath: Der vollständige Pfad der gelöschten Datei.
        """
        filename = os.path.basename(filepath)

        query_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.filename",
                    match=MatchValue(value=filename)
                )
            ]
        )

        try:
            points_to_delete = []
            offset = None
            batch_counter = 0
            MAX_BATCHES = 50  # Maximale Anzahl an Schleifendurchläufen

            while batch_counter < MAX_BATCHES:  # Begrenzung auf 50 Durchläufe
                print(f"Scrolle nach Vektoren für {filename}... (Batch {batch_counter})")

                scroll_result, next_offset = client.scroll(
                    collection_name=collection_name,
                    limit=1000,
                    scroll_filter=query_filter,
                    with_payload=False,
                    offset=offset  # Fix: Offset setzen!
                )

                if not scroll_result:
                    print("Keine weiteren Vektoren gefunden. Beende das Löschen.")
                    break

                new_ids = [point.id for point in scroll_result]
                print(f"🟢 Gefundene Vektoren in Batch {batch_counter}: {len(new_ids)}")

                points_to_delete.extend(new_ids)
                batch_counter += 1

                print(f"Nächster Offset-Wert: {next_offset}")  # Debugging: Offset anzeigen

                if next_offset is None:
                    print("Alle relevanten Vektoren wurden gefunden.")
                    break

                offset = next_offset if next_offset else None  # Explizit den Offset setzen!

            if batch_counter >= MAX_BATCHES:
                print(f"WARNUNG: Maximal {MAX_BATCHES} Batches erreicht! Vielleicht Endlosschleife?")

            if points_to_delete:
                print(f"Lösche {len(points_to_delete)} Vektoren für {filename}...")

                delete_response = client.delete(
                    collection_name=collection_name,
                    points_selector=points_to_delete
                )

                print(f"Erfolgreich gelöscht: {delete_response}")
            else:
                print(f"Keine Vektoren für {filename} gefunden.")

        except Exception as e:
            print(f"Fehler beim Löschen der Vektoren: {e}")


if __name__ == "__main__":
    event_handler = FileChangeHandler()
    observer = Observer()
    for folder in WATCHED_FOLDERS:
        observer.schedule(event_handler, folder, recursive=True)
    print("Überwachung gestartet...")
    observer.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
