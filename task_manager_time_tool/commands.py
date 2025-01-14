from db import add_task, start_task, stop_task, delete_task, list_tasks, report_tasks

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
        report_tasks(output_func)
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
        "  report                   - Zeige Zeitbuchungen + Summe\n"
        "  collwin                  - (Nur im GUI) Klappt das Ausgabefenster ein/aus\n"
        "  gui                      - Starte das GUI-Fenster\n"
        "  help                     - Zeige diese Hilfe an\n"
    )
    output_func(help_text)
