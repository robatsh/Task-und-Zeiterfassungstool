from db import add_task, start_task, stop_task, delete_task, list_tasks, report_tasks_filtered, export_report_to_html,os
from jinja2 import Template
from datetime import datetime

def handle_command(command_line, output_func=print):
    parts = command_line.split()
    if not parts:
        return

    cmd = parts[0].lower()
    args = parts[1:]

    if cmd == "help":
        show_help(output_func)
    elif cmd == "add":
        if len(args) < 1:
            output_func("Syntax: add <taskname> [minuten]")
        else:
            add_task(args[0], args[1] if len(args) > 1 else None, output_func)
    elif cmd == "start":
        if len(args) < 1:
            output_func("Syntax: start <taskname>")
        else:
            start_task(args[0], output_func)
    elif cmd == "stop":
        if len(args) < 1:
            output_func("Syntax: stop <taskname>")
        else:
            stop_task(args[0], output_func)
    elif cmd == "delete":
        if len(args) < 1:
            output_func("Syntax: delete <taskname>")
        else:
            delete_task(args[0], output_func)
    elif cmd == "list":
        list_tasks(output_func)
    elif cmd == "report":
        if len(args) == 0:
            report_tasks_filtered(output_func=output_func)
        else:
            start_date = None
            end_date = None
            task_name = None

            for arg in args:
                if arg.startswith("start="):
                    start_date = arg.split("=")[1]
                elif arg.startswith("end="):
                    end_date = arg.split("=")[1]
                elif arg.startswith("task="):
                    task_name = arg.split("=")[1]
                else:
                    output_func(f"Unbekanntes Argument: {arg}")

            report_tasks_filtered(start_date=start_date, end_date=end_date, task_name=task_name, output_func=output_func)
    elif cmd == "export":
        # Initialisiere Standardwerte
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = f"./report_{timestamp}.html"  # Standardpfad

        start_date = None
        end_date = None
        task_name = None

        # Prüfe, ob das erste Argument ein Dateipfad ist
        if len(args) > 0 and not args[0].startswith("start=") and not args[0].startswith("end=") and not args[0].startswith("task="):
            output_path = args[0]
            remaining_args = args[1:]  # Restliche Argumente
        else:
            remaining_args = args

        # Verarbeite die übrigen Argumente
        for arg in remaining_args:
            if arg.startswith("start="):
                start_date = arg.split("=", 1)[1]
            elif arg.startswith("end="):
                end_date = arg.split("=", 1)[1]
            elif arg.startswith("task="):
                task_name = arg.split("=", 1)[1]
            else:
                output_func(f"Unbekanntes Argument: {arg}")

        # Debug-Ausgabe für die übergebenen Werte
        output_func(f"Exportiere Bericht nach: {output_path}")
        output_func(f"Filter: start_date={start_date}, end_date={end_date}, task_name={task_name}")

        try:
            export_report_to_html(output_path, start_date=start_date, end_date=end_date, task_name=task_name)
        except Exception as e:
            output_func(f"Fehler beim Export: {e}")

    elif cmd == "collwin":
        output_func("Dieser Befehl ist nur in der GUI verfügbar.")
    else:
        output_func(f"Unbekannter Befehl: {cmd}")

def show_help(output_func=print):
    help_text = (
        "Verfügbare Befehle:\n"
        "  add <taskname> [min]     - Neuer Task (min=1..60: Mindest-Minuten)\n"
        "  start <taskname>         - Starte einen Task\n"
        "  stop <taskname>          - Stoppe einen Task\n"
        "  delete <taskname>        - Lösche einen Task (Sicherheitsabfrage)\n"
        "  list                     - Liste alle Tasks\n"
        "  report [args]            - Zeige Zeitbuchungen + Summe (Filter: start=, end=, task=)\n"
        "  export <path> [args]     - Exportiere Bericht als HTML (Filter: start=, end=, task=)\n"
        "  collwin                  - (Nur im GUI) Klappt das Ausgabefenster ein/aus\n"
        "  help                     - Zeige diese Hilfe an\n"
    )
    output_func(help_text)
