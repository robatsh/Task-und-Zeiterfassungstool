# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

## [Unreleased]
- Kleinere Fehlerbehebungen und Verbesserungen.

## - 2025-01-16
### Aktualisiert
- .gitignore Datei hinzugefügt(Wurde vergessen im Changelog zu erwähnen)

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
