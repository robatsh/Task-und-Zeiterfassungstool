# Task-und-Zeiterfassungstool-
Ein vielseitiges Task- und Zeiterfassungstool mit CLI- und NerdigerGUI-Funktionalität, das SQLite zur Speicherung verwendet. Ideal für persönliche oder kleine Projekt-Workflows.
Auch die GUI ist eine shell :)  
--
# Task Manager Tool

## Beschreibung

Ein vielseitiges Task- und Zeiterfassungstool mit einer benutzerfreundlichen CLI und einer minimalistischen GUI.

### Funktionen
- **CLI-Kommandos**
  - `add <taskname> [minuten]`: Neuen Task hinzufügen mit optionaler Mindestdauer pro Session.
  - `start <taskname>`: Startet einen Task.
  - `stop <taskname>`: Stoppt einen Task und speichert die Dauer der Session.
  - `delete <taskname>`: Löscht einen Task nach Bestätigung.
  - `list`: Zeigt eine Übersicht aller Tasks und deren Status.
  - `report`: Generiert einen Bericht über alle Sessions.
  - `collwin` (nur GUI): Klappt das Ausgabefeld ein oder aus.

- **NERD-GUI-Eigenschaften**
  - Schwarzer Hintergrund mit VGA-Orange (#ffb347) als Textfarbe.
  - Minimales Zeilen-Spacing für eine klare Übersicht.
  - <Tab>-Taste zur einfachen Autovervollständigung.
  - Minimieren statt Schließen durch das Fenster-Icon (X).
  - `exit`: Beendet die GUI und die Anwendung vollständig.
  
  ** Normale GUI Größe **
  - **Breite:** 600 Pixel
  - **Höhe:** 400 Pixel

  ** Eingeklappte Größe (`collwin`) **
  - **Breite:** 600 Pixel
  - **Höhe:** 100 Pixel

## GUI Screenshot
Hier ist ein Beispiel, wie die GUI aussieht:

![GUI Screenshot](assets/screen-gui.png)

- **Datenbank**
  - SQLite (tasks.db) speichert Tasks und Sessions.
  - Tabellenstruktur:
    - `tasks(id, name, is_running, current_start, minimum_minutes)`
    - `sessions(id, task_id, start, end, duration_sec)`

---

## Installation

### Voraussetzungen
- Python 3.7 oder neuer
- SQLite (kommt normalerweise mit Python)

### Installation
1. Klone dieses Repository:
   ```bash
   git clone https://github.com/username/task-manager-tool.git
   ```

2. Navigiere ins Projektverzeichnis:
   ```bash
   cd task-manager-tool
   ```

3. Starte das Programm:
   ```bash
   python3 main.py
   ```

---

## Verwendung

### CLI-Kommandos
Beispiele:
```bash
python3 main.py add "Task 1" 15
python3 main.py start "Task 1"
python3 main.py stop "Task 1"
python3 main.py report
```

### GUI starten
```bash
python3 main.py gui
```

---

## Lizenz

Dieses Projekt steht unter der **GNU General Public License v3.0 (GPL-3.0)**. Sie erlaubt:
- Private und kommerzielle Nutzung
- Modifikation und Weitergabe
- Open Source bleibt Pflicht, und die ursprüngliche Quelle muss genannt werden.

Details zur Lizenz findest du in der Datei `LICENSE`.

---

## Warnung
Dieses Projekt befindet sich noch in der Entwicklung. Der Einsatz erfolgt auf eigene Gefahr. Für Fehler oder Datenverlust wird keine Haftung übernommen.

---

## GitHub Setup

### Repository erstellen und initialisieren
1. **Erstelle ein neues Repository** auf GitHub mit dem Namen `task-manager-tool`.

2. **Lokales Repository initialisieren:**
   ```bash
   git init
   git add .
   git commit -m "Initial Commit: Task Manager Tool mit CLI- und GUI-Funktionalität"
   git branch -M main
   git remote add origin https://github.com/username/task-manager-tool.git
   git push -u origin main
   ```

### Weiterentwicklung
- Erstelle Pull Requests für Änderungen.
- Dokumentiere größere Änderungen im `CHANGELOG.md`.
