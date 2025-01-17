# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

## [1.2.0] - 2025-01-17
### Hinzugefügt
- **Neue GUI-Funktionalität:** Tray-Icon hinzugefügt, um die GUI zu minimieren und Aufgaben direkt über das Tray-Menü zu starten oder zu stoppen.
- **Tray-Icon-Callbacks:** Dynamisches Tray-Menü mit Task-Status und Aktionen.
- **Bootstrap-Integration:** HTML-Berichts-Template aktualisiert, um Bootstrap für ein modernes Styling zu nutzen.

### Aktualisiert
- **Template-Bericht:** Darstellung der HTML-Berichte mit Bootstrap-Tabellen für bessere Lesbarkeit und modernes Design.
- **Fehlermeldungen:** Verbesserte Fehlerbehandlung und Ausgabe bei nicht existierenden Tasks oder falschen Eingaben.
- **Kommando "collwin":** Befehl hinzugefügt, um die GUI-Ausgabe ein- und auszuklappen.

### Behoben
- **Datenbank-Initialisierung:** Sicherstellung, dass alle Tabellen korrekt erstellt werden, falls sie fehlen.
- **Fehlende Sicherheitsabfragen:** GUI-Sicherheitsabfragen für Task-Löschvorgänge hinzugefügt.

## [Unreleased]
- Kleinere Fehlerbehebungen und Verbesserungen.

## [1.1.0] - 2025-01-16
### Aktualisiert
- .gitignore Datei hinzugefügt

## [1.1.0] - 2025-01-15
### Hinzugefügt
- **Reporting-Filter:** Berichtsfunktionen erweitert, um Filter für `start=`, `end=` und `task=` zu unterstützen.
- **HTML-Export:** Möglichkeit, Berichte als HTML mit dynamischem Dateinamen (`report_<timestamp>.html`) zu exportieren.
- **Externe Template-Datei:** HTML-Template aus dem Code ausgelagert und in `template_report.html` integriert.
- **Installationsanweisungen:** Vollständige Installations- und Abhängigkeitsliste in das README aufgenommen.
- **Datenbank-Erstellung:** Hinweis hinzugefügt, dass die SQLite-Datenbank automatisch erstellt wird, wenn sie nicht vorhanden ist.

### Behoben
- Task-Filter im Reporting korrigiert, sodass Berichte nur die relevanten Tasks enthalten.
- Standardpfad-Handling für den Export, um Konflikte und unvollständige Angaben zu vermeiden.

## [1.0.0] - 2025-01-14
### Hinzugefügt
- **Task-Verwaltung:** CLI-Kommandos für `add`, `start`, `stop`, `delete`, `list` und `report`.
- **GUI:** Minimalistische GUI mit VGA-Orange (#ffb347) und CLI-ähnlicher Funktionalität.
- **SQLite-Datenbank:** Speicherung von Tasks und Sessions mit automatischer Verwaltung der Tabellenstruktur.

---

**Hinweis:** Änderungen an diesem Projekt werden in der [GitHub](https://github.com/robatsh/Task-und-Zeiterfassungstool detailliert dokumentiert.
