#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ein einfaches Task- und Zeiterfassungstool mit SQLite, CLI und GUI.
Python-Version: 3.7.3

Funktionen (CLI-Befehle):
  add <taskname> [minuten]  - Lege einen neuen Task an
                              minutes: (optional) Mindest-Minuten (1..60),
                                       wird bei jeder Session als Untergrenze gesetzt
  start <taskname>          - Starte einen Task
  stop <taskname>           - Stoppe einen Task (Speichert Dauer in einer Session)
  delete <taskname>         - Löscht einen Task (inkl. Sessions) nach Bestätigung
  list                      - Listet alle vorhandenen Tasks (Status: 'läuft' oder 'inaktiv')
  report                    - Zeigt alle Zeitbuchungen (Sessions) jedes Tasks inkl. Gesamtsumme
  collwin                   - (Nur im GUI) Klappt das Ausgabefenster weg (Toggle)
  gui                       - Startet ein kleines GUI-Fenster (Shell)
  help                      - Zeigt diese Hilfe an

GUI-Eigenschaften:
  - Schwarzer Hintergrund, VGA-Orange (#ffb347) als Textfarbe
  - Minimales Zeilen-Spacing
  - Oben/unten-Taste für History
  - <Tab>-Taste als einfache Autovervollständigung für "start ..." und "stop ..."
  - Unbekannte Befehle liefern "Unbekanntes Kommando."
  - Schließen-Icon (X) minimiert nur das Fenster
  - Befehl 'exit' schließt das Programm komplett
  - Der Cursor springt immer in das Eingabefeld (Entry), sobald das Fenster aktiv wird
  - Befehl 'collwin' klappt das Text-Ausgabefeld zusammen; tauchen Fehler oder Abbrüche auf,
    wird das Ausgabefeld wieder eingeblendet

Datenbank:
  tasks.db (SQLite)
  Tabellen:
    tasks(id, name, is_running, current_start, minimum_minutes)
    sessions(id, task_id, start, end, duration_sec)
"""

import sys
import os
import sqlite3
import datetime
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import tkinter.messagebox as messagebox

DB_NAME = "tasks.db"

def init_db():
    """Erstellt die SQLite-Datenbank (falls nicht vorhanden) und die benötigten Tabellen.
       Fügt die Spalte 'minimum_minutes' hinzu, falls sie noch nicht existiert.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Tabelle tasks
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        is_running INTEGER NOT NULL DEFAULT 0,
        current_start TIMESTAMP,
        minimum_minutes INTEGER NOT NULL DEFAULT 0
    )
    """)

    # Tabelle sessions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        start TIMESTAMP,
        end TIMESTAMP,
        duration_sec INTEGER,
        FOREIGN KEY(task_id) REFERENCES tasks(id)
    )
    """)

    # Versuch, die Spalte minimum_minutes nachträglich anzulegen, falls sie fehlt
    try:
        cur.execute("ALTER TABLE tasks ADD COLUMN minimum_minutes INTEGER NOT NULL DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

def add_task(taskname, minimum_str=None, output_func=print):
    """
    Fügt einen neuen Task hinzu. Falls eine Minutenangabe vorhanden ist,
    wird sie als Mindest-Minuten pro Session gespeichert (1..60).
    """
    # Default = 0 => sekunden-genau
    min_minutes = 0
    if minimum_str is not None:
        try:
            val = int(minimum_str)
            if val < 1:
                val = 0
            elif val > 60:
                val = 60
            min_minutes = val
        except ValueError:
            # Falls ungültig, bleibt min_minutes = 0
            pass

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Prüfen, ob Task schon existiert
    cur.execute("SELECT id FROM tasks WHERE name = ?", (taskname,))
    row = cur.fetchone()
    if row:
        output_func(f"Task '{taskname}' existiert bereits.")
        conn.close()
        return

    # Anlegen
    cur.execute(
        "INSERT INTO tasks (name, is_running, current_start, minimum_minutes) VALUES (?, 0, NULL, ?)",
        (taskname, min_minutes)
    )
    conn.commit()
    conn.close()
    if min_minutes > 0:
        output_func(f"Task '{taskname}' wurde angelegt (Mindest-Minuten: {min_minutes}).")
    else:
        output_func(f"Task '{taskname}' wurde angelegt (Sekundengenaue Aufzeichnung).")

def start_task(taskname, output_func=print):
    """Startet einen Task (setzt is_running=1, current_start=jetzt)."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT id, is_running FROM tasks WHERE name = ?", (taskname,))
    task_row = cur.fetchone()
    if not task_row:
        output_func(f"Task '{taskname}' existiert nicht.")
        conn.close()
        return

    task_id, is_running = task_row
    if is_running == 1:
        output_func(f"Task '{taskname}' läuft bereits.")
        conn.close()
        return

    now = datetime.datetime.now()
    cur.execute("UPDATE tasks SET is_running=1, current_start=? WHERE id=?", (now, task_id))
    conn.commit()
    conn.close()
    output_func(f"Task '{taskname}' wurde gestartet.")

def stop_task(taskname, output_func=print):
    """Stoppt einen Task und erzeugt einen Eintrag in sessions."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT id, is_running, current_start, minimum_minutes FROM tasks WHERE name = ?", (taskname,))
    task_row = cur.fetchone()
    if not task_row:
        output_func(f"Task '{taskname}' existiert nicht.")
        conn.close()
        return

    task_id, is_running, current_start, min_minutes = task_row
    if is_running == 0:
        output_func(f"Task '{taskname}' ist nicht aktiv.")
        conn.close()
        return

    now = datetime.datetime.now()

    if current_start is None:
        duration_sec = 0.0
    else:
        start_dt = datetime.datetime.fromisoformat(current_start)
        delta = now - start_dt
        duration_sec = float(delta.total_seconds())

    # Mindest-Minuten check
    if min_minutes > 0:
        min_seconds = min_minutes * 60
        if duration_sec < min_seconds:
            duration_sec = float(min_seconds)

    # Session-Eintrag
    cur.execute("""
        INSERT INTO sessions (task_id, start, end, duration_sec)
        VALUES (?, ?, ?, ?)
    """, (task_id, current_start, now, int(duration_sec)))

    # Task auf inaktiv setzen
    cur.execute("UPDATE tasks SET is_running=0, current_start=NULL WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    output_func(
        f"Task '{taskname}' wurde gestoppt. Dauer dieser Session: {format_duration(duration_sec)}."
    )

def delete_task_gui_interactive(taskname, output_func):
    """
    GUI-Variante: Fragt per Messagebox, ob der Task gelöscht werden soll.
    Gibt True zurück, wenn gelöscht wurde, False sonst.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT id FROM tasks WHERE name = ?", (taskname,))
    row = cur.fetchone()
    if not row:
        output_func(f"Task '{taskname}' existiert nicht.")
        conn.close()
        return False  # nichts gelöscht
    task_id = row[0]

    # Messagebox zum Bestätigen
    answer = messagebox.askyesno("Task löschen", f"Willst du wirklich den Task '{taskname}' löschen?")
    if answer:
        # Sessions löschen
        cur.execute("DELETE FROM sessions WHERE task_id=?", (task_id,))
        # Task löschen
        cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        conn.close()
        output_func(f"Task '{taskname}' wurde gelöscht.")
        return True
    else:
        conn.close()
        output_func("Löschen abgebrochen.")
        return False

def delete_task(taskname, output_func=print):
    """
    Löscht einen Task (inklusive seiner Sessions), nach Sicherheitsabfrage (y/n in CLI
    bzw. per Messagebox im GUI).
    """
    # CLI vs GUI unterscheiden wir an output_func
    if output_func == print:
        # --> CLI
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id FROM tasks WHERE name = ?", (taskname,))
        row = cur.fetchone()
        if not row:
            output_func(f"Task '{taskname}' existiert nicht.")
            conn.close()
            return
        task_id = row[0]

        confirm = input(f"Willst du wirklich den Task '{taskname}' löschen? (y/n) ").strip().lower()
        if confirm in ("y", "yes"):
            # Sessions löschen
            cur.execute("DELETE FROM sessions WHERE task_id=?", (task_id,))
            # Task löschen
            cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            conn.commit()
            conn.close()
            output_func(f"Task '{taskname}' wurde gelöscht.")
        else:
            conn.close()
            output_func("Löschen abgebrochen.")
    else:
        # --> GUI
        delete_task_gui_interactive(taskname, output_func=output_func)

def list_tasks(output_func=print):
    """Listet alle Tasks mit Status auf."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT name, is_running, minimum_minutes FROM tasks ORDER BY name ASC")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        output_func("Keine Tasks gefunden.")
        return

    output_func("Tasks:")
    for row in rows:
        name, is_running, min_minutes = row
        status = "läuft" if is_running == 1 else "inaktiv"
        if min_minutes > 0:
            output_func(f"  - {name} ({status}, Mindest-Minuten: {min_minutes})")
        else:
            output_func(f"  - {name} ({status}, sekunden-genau)")

def report_tasks(output_func=print):
    """
    Zeigt alle Zeitbuchungen pro Task (Start-/End-Zeit, Dauer)
    und danach jeweils die Gesamtdauer für den Task.
    Abschließend kommt eine Gesamt-Summe aller Tasks.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Alle Tasks abrufen
    cur.execute("SELECT id, name, is_running, minimum_minutes FROM tasks ORDER BY name ASC")
    tasks = cur.fetchall()

    if not tasks:
        output_func("Keine Tasks vorhanden.")
        conn.close()
        return

    output_func("Auswertung aller Zeitbuchungen:\n")
    grand_total = 0.0

    for task_id, name, is_running, min_minutes in tasks:
        output_func(f"=== Task: {name} ===")
        # Sessions laden
        cur.execute("""
            SELECT start, end, duration_sec
            FROM sessions
            WHERE task_id=?
            ORDER BY start ASC
        """, (task_id,))
        sessions = cur.fetchall()

        if not sessions:
            output_func("  Keine Sessions vorhanden.\n")
            continue

        task_sum = 0.0
        for start_str, end_str, duration_sec in sessions:
            start_dt = datetime.datetime.fromisoformat(start_str) if start_str else None
            end_dt = datetime.datetime.fromisoformat(end_str) if end_str else None

            if start_dt and end_dt:
                # DATUM + Uhrzeit, z. B. 2025-01-14 15:30:00
                start_fmt = start_dt.strftime("%Y-%m-%d %H:%M:%S")
                end_fmt = end_dt.strftime("%Y-%m-%d %H:%M:%S")
                output_func(f"  Session: {start_fmt} - {end_fmt} | Dauer: {format_duration(float(duration_sec))}")
            else:
                output_func(f"  Session: ??? - ??? | Dauer: {format_duration(float(duration_sec))}")

            task_sum += float(duration_sec)

        output_func(f"  Gesamtzeit für '{name}': {format_duration(task_sum)}\n")
        grand_total += task_sum

    # Abschluss: Gesamte Zeit aller Tasks
    output_func(f"Gesamte erfasste Zeit aller Tasks: {format_duration(grand_total)}\n")
    conn.close()

def format_duration(seconds):
    """Hilfsfunktion zum Formatieren von Sekunden als HH:MM:SS."""
    s = int(round(seconds))
    hours = s // 3600
    minutes = (s % 3600) // 60
    secs = s % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def get_task_suggestions(partial):
    """
    Liefert alle Task-Namen zurück, die mit 'partial' anfangen (Case-insensitiv).
    """
    partial = partial.lower()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT name FROM tasks")
    all_tasks = [row[0] for row in cur.fetchall()]
    conn.close()

    # Filtern
    suggestions = [t for t in all_tasks if t.lower().startswith(partial)]
    return suggestions

# -------------
# GUI-Implementierung
# -------------

class TaskGUI(tk.Tk):
    """
    Kleines 'Shell'-Fenster mit schwarzem Hintergrund,
    VGA-Orange als Textfarbe, History, minimalem Line-Spacing.
    'exit' beendet das Programm, das Schließen-Icon minimiert nur.
    """
    def __init__(self):
        super().__init__()
        self.title("Task Shell")
        self.configure(bg="black")

        # Beim Schließen nur minimieren, nicht wirklich beenden
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Collapsed-Status für das Ausgabefeld
        self.collapsed = False

        # Textausgabe
        self.output_box = scrolledtext.ScrolledText(self,
                                                    wrap=tk.WORD,
                                                    bg="black",
                                                    fg="#ffb347",
                                                    height=20,
                                                    padx=5,
                                                    pady=5)
        self.output_box.configure(font=("TkDefaultFont", 9))  # Minimales Line-Spacing
        self.output_box.pack(fill=tk.BOTH, expand=True)

        # Eingabezeile
        self.input_var = tk.StringVar()
        self.entry = tk.Entry(
            self,
            textvariable=self.input_var,
            bg="black",
            fg="#ffb347",
            insertbackground="#ffb347"
        )
        self.entry.configure(font=("TkDefaultFont", 9))
        self.entry.bind("<Return>", self.on_enter)
        self.entry.bind("<Up>", self.on_up)
        self.entry.bind("<Down>", self.on_down)
        self.entry.bind("<Tab>", self.on_tab)  # Tab-Completion
        self.entry.pack(fill=tk.X)

        # Den Fokus direkt auf das Eingabefeld setzen
        self.entry.focus_set()

        # Damit bei Klick auf das Fenster (bzw. wenn es aktiv wird) der Cursor weiter in der Eingabezeile bleibt:
        self.bind("<FocusIn>", lambda e: self.entry.focus_set())

        # History
        self.history = []
        self.history_index = -1

        # Begrüßungsnachricht
        self.print_line("Willkommen in der Task-Shell! Gib 'help' ein für mögliche Befehle.\n")

    def on_close(self):
        """Minimiert das Fenster anstatt die App zu beenden."""
        self.iconify()

    def on_enter(self, event=None):
        """Wird aufgerufen, wenn der Benutzer Enter drückt."""
        cmd = self.input_var.get().strip()
        self.print_line(f"> {cmd}")
        self.input_var.set("")  # Eingabe leeren

        if cmd:
            self.history.append(cmd)
            self.history_index = len(self.history)

        if cmd.lower() == "exit":
            self.print_line("Programm wird beendet...")
            self.destroy()
            sys.exit(0)
        else:
            handle_command(cmd, output_func=self.print_line)

        # Fokus erneut auf das Eingabefeld setzen
        self.entry.focus_set()

    def on_up(self, event=None):
        """History-Navigation nach oben."""
        if self.history and self.history_index > 0:
            self.history_index -= 1
            self.input_var.set(self.history[self.history_index])
            self.entry.icursor(tk.END)

    def on_down(self, event=None):
        """History-Navigation nach unten."""
        if self.history and self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.input_var.set(self.history[self.history_index])
            self.entry.icursor(tk.END)
        else:
            self.input_var.set("")
            self.history_index = len(self.history)

    def on_tab(self, event=None):
        """Einfache Autovervollständigung für 'start <task>' und 'stop <task>'."""
        current = self.input_var.get()
        parts = current.split()
        if len(parts) >= 2 and parts[0].lower() in ["start", "stop"]:
            # z.B. "start " + partial
            cmd_word = parts[0].lower()
            partial_task = " ".join(parts[1:])  # Falls der Taskname Leerzeichen enthalten könnte
            suggestions = get_task_suggestions(partial_task)

            if len(suggestions) == 1:
                # Eindeutige Vervollständigung
                new_cmd = cmd_word + " " + suggestions[0]
                self.input_var.set(new_cmd)
            elif len(suggestions) > 1:
                # Mehrere Treffer -> Liste anzeigen
                self.print_line(f"Mehrere Vorschläge: {', '.join(suggestions)}")

            # Verhindert, dass der Tab-Effekt (z.B. Fokus-Wechsel) einsetzt
            return "break"

        # Standard-Verhalten, wenn keine Autocomplete passend ist
        return None

    def print_line(self, text):
        """Gibt Text in der Ausgabe-Box aus. Bei Fehlern oder Abbrüchen wird das Feld eingeblendet."""
        # Wenn wir vor dem print eingeklappt sind und ein "Fehler" oder "abgebrochen" oder "unbekannt" auftaucht,
        # klappen wir es wieder aus.
        # Kleine, simple Prüfung: Wir checken einige Schlüsselwörter
        keywords = ["fehler", "unbekannt", "abgebrochen", "existiert nicht", "läuft bereits"]
        lower_text = text.lower()
        if any(kw in lower_text for kw in keywords):
            if self.collapsed:
                self.toggle_collapse(force_expand=True)

        self.output_box.insert(tk.END, text + "\n")
        self.output_box.see(tk.END)

    def toggle_collapse(self, force_expand=False):
        """Blendet das Ausgabe-Feld aus oder wieder ein."""
        if force_expand:
            # Nur ausklappen, falls es gerade eingeklappt war
            if self.collapsed:
                self.output_box.pack(fill=tk.BOTH, expand=True)
                self.collapsed = False
            return

        if self.collapsed:
            # Wieder einblenden
            self.output_box.pack(fill=tk.BOTH, expand=True)
            self.collapsed = False
        else:
            # Ausblenden
            self.output_box.pack_forget()
            self.collapsed = True

# -------------
# Zentrale Befehls-Logik
# -------------

def handle_command(command_line, output_func=print):
    """
    Zentrale Verarbeitung eines Befehls sowohl für CLI als auch für GUI.
    `output_func` ist eine Funktion zum Ausgeben von Text (z. B. print oder gui.print_line).
    """
    parts = command_line.split()
    if not parts:
        return

    cmd = parts[0].lower()
    args = parts[1:]

    if cmd == "help":
        show_help(output_func)
    elif cmd == "add":
        if not args:
            output_func("Bitte Tasknamen angeben. Syntax: add <taskname> [minuten]")
            return
        elif len(args) == 1:
            # Nur Taskname
            taskname = args[0]
            add_task(taskname, None, output_func=output_func)
        else:
            # Taskname + Minuten
            taskname = args[0]
            minutes_str = args[1]
            add_task(taskname, minutes_str, output_func=output_func)

    elif cmd == "start":
        if not args:
            output_func("Bitte Tasknamen angeben. Syntax: start <taskname>")
            return
        taskname = " ".join(args)
        start_task(taskname, output_func=output_func)

    elif cmd == "stop":
        if not args:
            output_func("Bitte Tasknamen angeben. Syntax: stop <taskname>")
            return
        taskname = " ".join(args)
        stop_task(taskname, output_func=output_func)

    elif cmd == "delete":
        if not args:
            output_func("Bitte Tasknamen angeben. Syntax: delete <taskname>")
            return
        taskname = " ".join(args)
        delete_task(taskname, output_func=output_func)

    elif cmd == "list":
        list_tasks(output_func=output_func)

    elif cmd == "report":
        report_tasks(output_func=output_func)

    elif cmd == "collwin":
        # Nur im GUI sinnvoll
        if output_func == print:
            output_func("Dieser Befehl ist nur in der GUI verfügbar.")
        else:
            # Wir haben im GUI den "print_line" => Das ist eine bound method, wir müssen sie auf self ermitteln.
            # Trick: die Bound-Method hat im __self__-Attribut das Objekt. => output_func.__self__ ist der TaskGUI-Instanz
            gui_instance = output_func.__self__
            if hasattr(gui_instance, "toggle_collapse"):
                gui_instance.toggle_collapse()
            else:
                output_func("Fenster kann nicht geklappt werden.")
    else:
        output_func("Unbekanntes Kommando.")

def show_help(output_func=print):
    """Zeigt Hilfe/Kommandoliste an."""
    help_text = (
        "Verfügbare Befehle:\n"
        "  help                     - Zeigt diese Hilfe an\n"
        "  add <taskname> [min]     - Neuer Task (min=1..60: Mindest-Minuten)\n"
        "  start <taskname>         - Starte einen Task\n"
        "  stop <taskname>          - Stoppe einen Task\n"
        "  delete <taskname>        - Lösche einen Task (Sicherheitsabfrage)\n"
        "  list                     - Liste alle Tasks\n"
        "  report                   - Zeige Zeitbuchungen + Summe\n"
        "  collwin                  - (Nur im GUI) Klappt das Ausgabefenster ein/aus\n"
        "  gui                      - Starte das GUI-Fenster\n"
        "  exit                     - (Nur im GUI) Beendet das Programm\n"
    )
    output_func(help_text)

def main():
    """Haupteinstiegspunkt für die CLI."""
    init_db()

    # Kleine Willkommensnachricht, wenn keine Argumente vorhanden
    if len(sys.argv) < 2:
        print("Willkommen im Task- und Zeiterfassungstool!")
        print("Nutze 'help' für eine Liste der verfügbaren Befehle.\n")
        return

    command = sys.argv[1].lower()
    # Alle restlichen Argumente
    # (Beim CLI-Aufruf wie "python tasks.py add MeineAufgabe 15")
    # => command="add", args=["MeineAufgabe", "15"]
    args = sys.argv[2:]

    if command == "help":
        show_help()
    elif command == "gui":
        # GUI starten
        app = TaskGUI()
        app.mainloop()
    else:
        # Alle anderen Befehle über handle_command
        # output_func=print => CLI
        line = " ".join(sys.argv[1:])  # "add Foo 15" etc.
        handle_command(line, output_func=print)

if __name__ == "__main__":
    main()
