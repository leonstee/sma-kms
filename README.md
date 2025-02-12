# SMA-KMS

SMA-KMS ist ein Tool zur Verwaltung und Verarbeitung von Wissensdaten mit Hilfe von KI-Modellen.

## Installation

### Voraussetzungen
- Python 3.8 oder neuer
- [pip](https://pip.pypa.io/en/stable/)

### Einrichtung

1. Klone das Repository:
   ```bash
   git clone https://github.com/leonstee/sma-kms.git
   cd sma-kms
   ```

2. Installiere die Abhängigkeiten:
   ```bash
   pip install -r requirements.txt
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

## Was funktioniert aktuell?

- Der Chat funktioniert bereits.
- Antworten werden als Stream ausgegeben
- Die Zitatfunktion ist implementiert, aber die Ergebnisse sind noch nicht perfekt. Bei passender Formulierung sind sie jedoch brauchbar.
- Grundlegendes Einlesen einer Datei

## Was gibt es noch zu tun?

- Chat History / Verlauf implementieren.
- Prompt für Antworten & Zitate anpassen.
- Eventuell die Erstellung der Datenbank-Queries mit einem extra Language Model (LM) umsetzen.
- Optimierung des Einleseprozesses für größere Datenmengen


