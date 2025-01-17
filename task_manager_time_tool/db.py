# db.py
import sqlite3
import datetime
import os
from jinja2 import Template

DB_NAME = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        is_running INTEGER NOT NULL DEFAULT 0,
        current_start TIMESTAMP,
        minimum_minutes INTEGER NOT NULL DEFAULT 0
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        start TIMESTAMP,
        end TIMESTAMP,
        duration_sec INTEGER,
        FOREIGN KEY(task_id) REFERENCES tasks(id)
    )""")
    conn.commit()
    conn.close()

def add_task(taskname, minimum_str=None, output_func=print):
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
            pass

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id FROM tasks WHERE name = ?", (taskname,))
    if cur.fetchone():
        output_func(f"Task '{taskname}' existiert bereits.")
        conn.close()
        return

    cur.execute(
        "INSERT INTO tasks (name, is_running, current_start, minimum_minutes) VALUES (?, 0, NULL, ?)",
        (taskname, min_minutes)
    )
    conn.commit()
    conn.close()
    output_func(f"Task '{taskname}' wurde angelegt (Mindest-Minuten: {min_minutes}).")

def start_task(taskname, output_func=print):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, is_running FROM tasks WHERE name = ?", (taskname,))
    task_row = cur.fetchone()
    if not task_row:
        output_func(f"Task '{taskname}' existiert nicht.")
        conn.close()
        return

    task_id, is_running = task_row
    if is_running:
        output_func(f"Task '{taskname}' läuft bereits.")
        conn.close()
        return

    now = datetime.datetime.now()
    cur.execute("UPDATE tasks SET is_running = 1, current_start = ? WHERE id = ?", (now, task_id))
    conn.commit()
    conn.close()
    output_func(f"Task '{taskname}' wurde gestartet.")

def stop_task(taskname, output_func=print):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, is_running, current_start, minimum_minutes FROM tasks WHERE name = ?", (taskname,))
    task_row = cur.fetchone()
    if not task_row:
        output_func(f"Task '{taskname}' existiert nicht.")
        conn.close()
        return

    task_id, is_running, current_start, min_minutes = task_row
    if not is_running:
        output_func(f"Task '{taskname}' ist nicht aktiv.")
        conn.close()
        return

    now = datetime.datetime.now()
    start_time = datetime.datetime.fromisoformat(current_start)
    duration = (now - start_time).total_seconds()

    # Mindest-Minuten berücksichtigen
    duration = max(duration, min_minutes * 60)

    cur.execute(
        "INSERT INTO sessions (task_id, start, end, duration_sec) VALUES (?, ?, ?, ?)",
        (task_id, current_start, now, int(duration))
    )
    cur.execute("UPDATE tasks SET is_running = 0, current_start = NULL WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    output_func(f"Task '{taskname}' wurde gestoppt. Dauer: {duration / 60:.2f} Minuten.")

def delete_task(taskname, output_func=print, is_gui=False):
    """
    Löscht den Task direkt, ohne MessageBox.
    Die Sicherheitsabfrage übernehmen wir in der GUI (pending_delete).
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id FROM tasks WHERE name = ?", (taskname,))
    task_row = cur.fetchone()
    if not task_row:
        output_func(f"Task '{taskname}' existiert nicht.")
        conn.close()
        return

    # Hier KEINE Interaktion mit tkinter.messagebox oder input().
    # Wir verlassen uns darauf, dass GUI/CLI bereits "y" abgefragt hat.
    task_id = task_row[0]
    cur.execute("DELETE FROM sessions WHERE task_id = ?", (task_id,))
    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    output_func(f"Task '{taskname}' wurde gelöscht.")

def list_tasks(output_func=print):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT name, is_running, minimum_minutes FROM tasks")
    tasks = cur.fetchall()
    conn.close()

    if not tasks:
        output_func("Keine Tasks vorhanden.")
        return

    for name, is_running, min_minutes in tasks:
        status = "läuft" if is_running else "inaktiv"
        output_func(f"Task: {name}, Status: {status}, Mindest-Minuten: {min_minutes}")

def report_tasks_filtered(start_date=None, end_date=None, task_name=None, output_func=print):
    """
    Generiert einen Bericht basierend auf optionalem Zeitraum und Task.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    task_filter = ""
    params = []

    if task_name:
        task_filter += " AND t.name = ?"
        params.append(task_name)

    if start_date:
        task_filter += " AND s.start >= ?"
        params.append(start_date)

    if end_date:
        task_filter += " AND s.end <= ?"
        params.append(end_date)

    query = f"""
        SELECT t.name, s.start, s.end, s.duration_sec
        FROM tasks t
        JOIN sessions s ON t.id = s.task_id
        WHERE 1=1 {task_filter}
        ORDER BY s.start ASC
    """

    cur.execute(query, params)
    sessions = cur.fetchall()
    conn.close()

    if not sessions:
        output_func("Keine Sitzungen gefunden.")
        return

    output_func("Bericht:")
    for tname, start, end, duration_sec in sessions:
        duration_min = duration_sec / 60
        output_func(f"Task: {tname}, Start: {start}, Ende: {end}, Dauer: {duration_min:.2f} Minuten")

def export_report_to_html(output_path=None, start_date=None, end_date=None, task_name=None):
    """
    Exportiert den Bericht als HTML.
    """
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    if not output_path:
        output_path = f"./report_{timestamp}.html"

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    task_filter = ""
    params = []

    if task_name:
        task_filter += " AND t.name = ?"
        params.append(task_name)

    if start_date:
        task_filter += " AND s.start >= ?"
        params.append(start_date)

    if end_date:
        task_filter += " AND s.end <= ?"
        params.append(end_date)

    query = f"""
        SELECT t.name, s.start, s.end, s.duration_sec
        FROM tasks t
        JOIN sessions s ON t.id = s.task_id
        WHERE 1=1 {task_filter}
        ORDER BY s.start ASC
    """

    cur.execute(query, params)
    sessions = cur.fetchall()
    conn.close()

    if not sessions:
        print("Keine Sitzungen gefunden.")
        return

    # Template laden
    try:
        with open("template_report.html", "r", encoding="utf-8") as template_file:
            template_content = template_file.read()
    except FileNotFoundError:
        print("Template-Datei 'template_report.html' wurde nicht gefunden.")
        return

    template = Template(template_content)
    html_content = template.render(sessions=sessions)

    if os.path.exists(output_path):
        print(f"Die Datei '{output_path}' existiert bereits. Bericht wird nicht überschrieben.")
        return

    with open(output_path, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)

    print(f"Bericht wurde erfolgreich als HTML exportiert: {output_path}")
