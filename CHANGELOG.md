# Changelog

Alle wichtigen �nderungen an diesem Projekt werden in dieser Datei dokumentiert.

## [Unreleased]
- Kleinere Fehlerbehebungen und Verbesserungen.

## - 2025-01-16
### Aktualisiert
- .gitignore Datei hinzugef�gt(Wurde vergessen im Changelog zu erw�hnen)

## [1.1.0] - 2025-01-15
### Hinzugef�gt
- **Reporting-Filter:** Berichtsfunktionen erweitert, um Filter f�r `start=`, `end=` und `task=` zu unterst�tzen.
- **HTML-Export:** M�glichkeit, Berichte als HTML mit dynamischem Dateinamen (`report_<timestamp>.html`) zu exportieren.
- **Externe Template-Datei:** HTML-Template aus dem Code ausgelagert und in `template_report.html` integriert.
- **Installationsanweisungen:** Vollst�ndige Installations- und Abh�ngigkeitsliste in das README aufgenommen.
- **Datenbank-Erstellung:** Hinweis hinzugef�gt, dass die SQLite-Datenbank automatisch erstellt wird, wenn sie nicht vorhanden ist.

### Behoben
- Task-Filter im Reporting korrigiert, sodass Berichte nur die relevanten Tasks enthalten.
- Standardpfad-Handling f�r den Export, um Konflikte und unvollst�ndige Angaben zu vermeiden.

## [1.0.0] - 2025-01-14
### Hinzugef�gt
- **Task-Verwaltung:** CLI-Kommandos f�r `add`, `start`, `stop`, `delete`, `list` und `report`.
- **GUI:** Minimalistische GUI mit VGA-Orange (#ffb347) und CLI-�hnlicher Funktionalit�t.
- **SQLite-Datenbank:** Speicherung von Tasks und Sessions mit automatischer Verwaltung der Tabellenstruktur.

---

**Hinweis:** �nderungen an diesem Projekt werden in der [GitHub](https://github.com/robatsh/Task-und-Zeiterfassungstool detailliert dokumentiert.
