# commands.py
from db import (
    add_task,
    start_task,
    stop_task,
    delete_task,
    list_tasks,
    report_tasks_filtered,
    export_report_to_html,
)
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
            # Normalfall: CLI ruft delete_task direkt auf,
            # aber in der GUI machen wir die Bestätigung anders.
            delete_task(args[0], output_func=output_func, is_gui=False)

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
        # Standard-Pfad und Timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = f"./report_{timestamp}.html"

        start_date = None
        end_date = None
        task_name = None

        # Prüfen, ob das erste Argument ein Pfad ist
        if len(args) > 0 and not any(args[0].startswith(x) for x in ("start=", "end=", "task=")):
            output_path = args[0]
            remaining_args = args[1:]
        else:
            remaining_args = args

        for arg in remaining_args:
            if arg.startswith("start="):
                start_date = arg.split("=", 1)[1]
            elif arg.startswith("end="):
                end_date = arg.split("=", 1)[1]
            elif arg.startswith("task="):
                task_name = arg.split("=", 1)[1]
            else:
                output_func(f"Unbekanntes Argument: {arg}")

        output_func(f"Exportiere Bericht nach: {output_path}")
        output_func(f"Filter: start_date={start_date}, end_date={end_date}, task_name={task_name}")

        try:
            export_report_to_html(output_path, start_date=start_date, end_date=end_date, task_name=task_name)
        except Exception as e:
            output_func(f"Fehler beim Export: {e}")

    elif cmd == "collwin":
        # Dieser Befehl soll im GUI eine Aktion auslösen,
        # in der CLI nur eine Meldung ausgeben.
        output_func("Dieser Befehl ist nur in der GUI verfügbar.")

    else:
        output_func(f"Unbekannter Befehl: {cmd}")


def show_help(output_func=print):
    help_text = (
        "Verfügbare Befehle:\n"
        "  add <taskname> [min]     - Neuer Task (min=1..60)\n"
        "  start <taskname>         - Starte einen Task\n"
        "  stop <taskname>          - Stoppe einen Task\n"
        "  delete <taskname>        - Lösche einen Task\n"
        "  list                     - Liste alle Tasks\n"
        "  report [start=.. end=.. task=..] - Bericht anzeigen\n"
        "  export <path> [start=.. end=.. task=..] - Bericht als HTML exportieren\n"
        "  collwin                  - (Nur im GUI) Klappt das Fenster ein/aus\n"
        "  help                     - Zeige diese Hilfe an\n"
    )
    output_func(help_text)
