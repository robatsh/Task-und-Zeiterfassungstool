import sqlite3
import tkinter.messagebox as messagebox
import datetime

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
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id FROM tasks WHERE name = ?", (taskname,))
    task_row = cur.fetchone()
    if not task_row:
        output_func(f"Task '{taskname}' existiert nicht.")
        conn.close()
        return

    if is_gui:
        confirm = messagebox.askyesno("Task löschen", f"Willst du den Task '{taskname}' wirklich löschen?")
    else:
        confirm_input = input(f"Willst du den Task '{taskname}' wirklich löschen? (y/n): ").strip().lower()
        confirm = confirm_input in ["y", "yes"]

    if confirm:
        task_id = task_row[0]
        cur.execute("DELETE FROM sessions WHERE task_id = ?", (task_id,))
        cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        output_func(f"Task '{taskname}' wurde gelöscht.")
    else:
        output_func("Löschen abgebrochen.")

    conn.close()

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

def report_tasks(output_func=print):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, name, minimum_minutes FROM tasks")
    tasks = cur.fetchall()

    if not tasks:
        output_func("Keine Tasks vorhanden.")
        conn.close()
        return

    for task_id, name, min_minutes in tasks:
        output_func(f"Task: {name} (Mindest-Minuten: {min_minutes})")
        cur.execute("SELECT start, end, duration_sec FROM sessions WHERE task_id = ?", (task_id,))
        sessions = cur.fetchall()
        for start, end, duration in sessions:
            adjusted_duration = max(duration, min_minutes * 60)
            output_func(f"  Start: {start}, Ende: {end}, Dauer: {adjusted_duration / 60:.2f} Minuten")

    conn.close()
