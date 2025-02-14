# SMA-KMS

SMA-KMS ist ein Tool zur Verwaltung und Verarbeitung von Wissensdaten mit Hilfe von KI-Modellen.

## Installation

### Voraussetzungen
- Python 3.8 oder neuer
- [pip](https://pip.pypa.io/en/stable/)
- Ollama-Instanz
- Qdrant-Vektordatenbank

### Einrichtung

1. Klone das Repository:
   ```bash
   git clone https://github.com/leonstee/sma-kms.git
   cd sma-kms
   ```

2. Installiere die Abhängigkeiten:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. Kopiere die `.env.example` Datei und passe sie an:
   ```bash
   cp .env.example .env
   ```
   Bearbeite die `.env` Datei nach Bedarf. Standardwerte:
   ```ini
   QDRANT_COLLECTION=sma-kms
   OLLAMA_HOST=http://localhost:11434
   LM_MODEL=llama3.2
   EMBEDDING_MODEL=bge-m3
   QDRANT_URL=http://localhost:6333
   ```

### Empfohlenes Language Model

Folgendes Language Model wird empfohlen: qwen2.5:7b-instruct
```bash
ollama pull qwen2.5:7b-instruct
```
Grund: Eine Websuche wird dann durchgeführt, wenn das LM *"Frage leider nicht beantworten"* erwähnt.
Die meisten anderen Modelle befolgen die Aufforderung, diese Ausgabe bei unzureichenden Informationen zu tätigen, nicht oder nur in abgewandeltem Wortlaut.


## Datenvorbereitung

Bevor das Projekt genutzt werden kann, muss die Datei `load_data.py` **einmalig** ausgeführt werden:
```bash
python load_data.py
```
⚠ **Wichtig:** Diese Datei sollte nicht mehrmals ausgeführt werden, um doppelte oder fehlerhafte Daten zu vermeiden.

## Starten der Anwendung

Um die Anwendung zu starten, führe die folgende Datei aus:
```bash
python gradio_ui.py
```
Dadurch wird die Benutzeroberfläche von SMA-KMS gestartet.

## Bestehende Funktionen:
- Standard-Chat ist funktionsfähig
- Antworten werden als Stream ausgegeben
- Zitatfunktion ist integriert
- Web-Suche bei fehlenden Informationen in den vorhandenen Dokumenten
- Grundlegendes Einlesen von Dateien
- Automatische Aufnahme von Dokumenten aus Zotero, Obsidian und lokalen Dateien in die Vektordatenbank
- Priorisierung von Dokumenten aus verschiedenen Quellen

## Mögliche Erweiterungen und Verbesserungen
- Chat-Kontext-History für eine kohärente Interaktion speichern
- Web-Interface für Einstellungen (z. B. Priorisierung, Datei-Pfade)
- In-Chat Datei-Upload mit In-Memory-Datenbank
- Optimierung des Embedding-Modells
- OCR- und Bildanalyse integrieren
- Effiziente Aktualisierung der Vektoren bei Dateiänderungen, statt vollständigem Löschen und dann wiedereinfügen

