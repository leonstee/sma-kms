# 🚀 SMA-KMS

SMA-KMS ist ein **lokal betriebenes**, KI-gestütztes Wissensmanagementsystem (KMS), das wissenschaftliche Dokumente 📄, persönliche Notizen 📝 und externe Webquellen 🌍 integriert, um effiziente Recherchen und Analysen zu ermöglichen. Es nutzt moderne Open-Source-Technologien wie Large Language Models (LLMs) und Vektorendatenbanken.  Der Hauptanwendungsbereich ist das Information Security Management, insbesondere für Compliance, wobei es zur Verwaltung sicherheitsrelevanter Informationen und zur Unterstützung von Sicherheitsanalysen eingesetzt werden kann.

---

## 🛠 Installation

### 🚀 Schnelle Einrichtung mit Docker

#### ✅ Voraussetzungen

- 🖥 **Git**
- 🐳 **Docker & Docker Compose**
- 🧠 **laufende Ollama-Instanz** (Installation [hier](https://ollama.ai) verfügbar)

1. **Klone das Repository:**

   ```bash
   git clone https://github.com/leonstee/sma-kms.git
   cd sma-kms
   ```

2. **Kopiere die ********************`.env.example`******************** Datei und passe sie an:**

   ```bash
   cp .env.example .env
   ```

   Die folgenden Variablen **müssen** angepasst werden:

   - `ZOTERO_STORAGE_FOLDER` (Pfad zum Zotero-Speicherordner)
   - `OBSIDIAN_MD_FOLDER` (Pfad zum Obsidian-Markdown-Ordner)
   - `LOCAL_PDF_FOLDER` (Pfad zu allen gewünschten lokalen PDFs)

   Die folgenden Variablen **können** je nach Bedarf angepasst werden:

   - `OLLAMA_HOST` (Ollama-Adresse, falls nicht der Standardport genutzt wird)
   - `LM_MODEL` (verwendetes Large Language Model)
   - `EMBEDDING_MODEL` (Modell zur Vektorisierung von Texten)
   - `QDRANT_COLLECTION` (Name der Sammlung in der Vektordatenbank)
  
   Die Variable `QDRANT_URL` wird im Docker-Betrieb nicht genutzt.
  
3. **Lade das empfohlene Language Model herunter und starte Ollama:**

   ```bash
   ollama pull qwen2.5:7b-instruct
   ollama pull bge-m3
   ollama serve
   ```

4. **Erstelle und starte die Container:**

   ```bash
   docker-compose up -d --build
   ```

5. **Öffne die Benutzeroberfläche:**
   Sobald die Container gestartet sind, kann das Webinterface über `http://localhost:7860` 🌐 aufgerufen werden.

---

### 🔧 Einrichtung für Entwicklung

#### ✅ Voraussetzungen

- 🖥 **Git**
- 🐍 **Python 3.8 oder neuer**
- 📦 **pip** (für Paketverwaltung)
- 📂 **Qdrant-Vektordatenbank** (Installation [hier](https://qdrant.tech/documentation/quickstart/) verfügbar)
- 🧠 **laufende Ollama-Instanz** (Installation [hier](https://ollama.ai) verfügbar)

Falls du SMA-KMS ohne Docker lokal einrichten möchtest, folge diesen Schritten:

1. **Klone das Repository:**

   ```bash
   git clone https://github.com/leonstee/sma-kms.git
   cd sma-kms
   ```

2. 📦 Installiere die benötigten Abhängigkeiten:

   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. 📑 Kopiere die `.env.example` Datei und passe sie an:

   ```bash
   cp .env.example .env
   ```


4. ⚙ **Anpassung der ********************************************`config.py`******************************************** Datei:**

   - Falls SMA-KMS innerhalb von Docker betrieben wird, sind die vordefinierten Pfade in `config.py` (`/zotero`, `/obsidian`, `/pdfs`) korrekt.
   - Für lokale Entwicklung müssen stattdessen die entsprechenden Umgebungsvariablen aus `.env` genutzt werden. Hierbei sollten die auskommentierten Alternativen in `config.py` aktiviert werden.

5. 📂 **Qdrant-Datenbank starten:**
   SMA-KMS benötigt eine **Qdrant-Datenbank** für die Vektorensuche. Falls Qdrant nicht bereits als Dienst läuft, kann es mit folgendem Docker-Befehl gestartet werden:

   ```bash
   docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
   ```


6. 📥 Lade das empfohlene Language Model herunter und starte Ollama:

   ```bash
   ollama pull qwen2.5:7b-instruct
   ollama pull bge-m3
   ollama serve
   ```

7. ▶ **Starte die Anwendung:**

   ```bash
   python gradio_ui.py
   ```

8. ▶ **Starte den Datei-Überwachungsdienst:**
   Damit Änderungen an den gespeicherten Dateien automatisch erkannt und verarbeitet werden, muss folgendes Skript ausgeführt werden:

   ```bash
   python watching.py
   ```

9. **Öffne die Benutzeroberfläche:**
   Sobald die Container gestartet sind, kann das Webinterface über `http://localhost:7860` 🌐 aufgerufen werden.

---

## 📂 Datenvorbereitung

Nach der Einrichtung müssen bestehende Dateien manuell eingelesen werden. Dazu wird im **Gradio Interface** der Button **"Vorhandene Dateien einlesen"** gedrückt. Danach erkennt das System **neue, geänderte oder gelöschte Dateien** automatisch und verarbeitet diese entsprechend. ✅

---

## 🌟 Vorteile von lokalem Betrieb & Open Source Technologien

### 🔐 **Datenschutz & Sicherheit**

Da das System vollständig lokal betrieben wird, bleiben alle Daten auf dem eigenen Rechner und werden nicht in die Cloud hochgeladen. Dies stellt sicher, dass sensible Informationen geschützt bleiben und keine Abhängigkeit von externen Diensten besteht.

### 🛠 **Anpassbarkeit & Kontrolle**

Durch den Einsatz von Open-Source-Technologien kann das System individuell angepasst werden. Benutzer\:innen haben vollständige Kontrolle über die genutzten Modelle, Datenquellen und Integrationen.

### 🚀 **Keine Abhängigkeit von Drittanbietern**

Da keine proprietären Cloud-Dienste benötigt werden, kann das System unabhängig von kommerziellen Anbietern betrieben werden. Dies spart Kosten und ermöglicht langfristige Nachhaltigkeit.

### ⚡ **Performance & Offline-Verfügbarkeit**

Lokaler Betrieb ermöglicht schnelle Antwortzeiten und die Möglichkeit, das System auch ohne Internetverbindung zu nutzen.

---

## 🔧 Mögliche Erweiterungen & Verbesserungen

- 🛠 **Docker-Compose-Profil für Ollama:** Ein zusätzlicher Profilmodus in der `docker-compose.yml`, der Ollama direkt in Docker installiert und automatisch die benötigten Images herunterlädt.
- 🗂 **Chat-Kontext-History speichern:** Für eine kohärente und kontextbezogene Interaktion mit dem System.
- 🎛 **Web-Interface für Einstellungen:** Anpassungen wie Priorisierung von Quellen oder Dateipfade über eine intuitive Benutzeroberfläche ermöglichen.
- 📤 **In-Chat Datei-Upload:** Direkte Verarbeitung hochgeladener Dokumente mithilfe einer In-Memory-Datenbank.
- 🏎 **Optimierung des Embedding-Modells:** Verbesserung der Suchgenauigkeit und Effizienz durch feinere Abstimmung der Embeddings.
- 🖼 **OCR- und Bildanalyse:** Integration zur Verarbeitung und Durchsuchbarkeit von gescannten Dokumenten und Bildern.
- 🔄 **Effiziente Vektoren-Aktualisierung:** Änderungen an Dateien automatisch erkennen und aktualisieren, anstatt komplette Neuberechnungen durchzuführen.
- 🎨 **Verbesserte UI/UX:** Eine moderne und intuitive Benutzeroberfläche für eine angenehmere Nutzung.

## 🛠 Typische Fehler & deren Behebung

### ❌ Fehler: Ollama läuft nicht

**Lösung:**

- Prüfe, ob der Ollama-Dienst aktiv ist:
  ```bash
  ps aux | grep ollama
  ```
- Falls Ollama nicht läuft, starte den Dienst mit:
  ```bash
  ollama serve
  ```
- Falls Ollama nicht läuft, aber nicht erreichbar ist:
     - Überprüfe mit `ollama serve`, ob Ollama den Standardport 11434 nutzt.
     - Passe gegebenenfalls `OLLAMA_HOST` in der `.env`-Datei an
- Falls der Fehler weiterhin besteht, installiere Ollama neu ([Installationsseite](https://ollama.ai)).

### ❌ Fehler: Docker-Netzwerk "kms" wurde nicht automatisch erstellt

**Lösung:**

- Prüfe, ob das Netzwerk existiert:
  ```bash
  docker network ls | grep kms
  ```
- Falls es fehlt, erstelle das Netzwerk manuell:
  ```bash
  docker network create kms
  ```
- Starte anschließend die Container neu:
  ```bash
  docker-compose down && docker-compose up -d --build
  ```

### ❌ Fehler: Container starten nicht oder stürzen ab

**Lösung:**

- Prüfe die Logs mit:
  ```bash
  docker logs container_name
  ```
- Stelle sicher, dass keine Ports blockiert sind (`docker ps` zeigt laufende Container an).
- Versuche, alle Container neu zu starten:
  ```bash
  docker-compose down && docker-compose up -d --build
  ```

### ❌ Fehler: `ollama`-Befehl wird nicht erkannt

**Lösung:**

- Stelle sicher, dass **Ollama** installiert ist ([Installationsseite](https://ollama.ai)).
- Führe `ollama serve` aus, um den Dienst zu starten.

### ❌ Fehler: Qdrant-Datenbank nicht erreichbar

**Lösung:**

- Prüfe, ob Qdrant läuft:
  ```bash
  docker ps | grep qdrant
  ```
- Falls nicht, starte Qdrant manuell:
  ```bash
  docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
  ```

### ❌ Fehler: `python watching.py` erkennt keine Änderungen

**Lösung:**

- Stelle sicher, dass die `.env`-Variablen korrekt gesetzt sind.
- Prüfe, ob die zu überwachenden Ordner existieren und korrekt angegeben sind (`ZOTERO_STORAGE_FOLDER`, `OBSIDIAN_MD_FOLDER`, `LOCAL_PDF_FOLDER`).

### ❌ Fehler: Fehlende oder falsche Antworten des Chatbots

**Lösung:**

- Stelle sicher, dass `ollama serve` läuft und die richtigen Modelle geladen wurden.
- Überprüfe, ob Qdrant korrekt eingerichtet wurde und eine Indexierung stattgefunden hat.
- Überprüfe im [Qdrant-Dashboard](http://localhost:6333/dashboard), ob die Collection angelegt und Einträge angelegt wurden.
- Falls nötig, befülle die Datenbank erneut mit einem Klick auf den Button "vorhandene Dateien Einlesen" im [Chat-Interface](http://localhost:7860).

## 🎯 Fazit

SMA-KMS bietet eine **leistungsfähige, lokal betriebene** Lösung für KI-gestütztes Wissensmanagement mit **hoher Anpassbarkeit** und **Datenschutz**. Durch den Einsatz moderner **Open-Source-Technologien** ist das System **flexibel erweiterbar** und praxisnah nutzbar. 🏆



