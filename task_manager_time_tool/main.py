# main.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from db import init_db
from commands import handle_command
from gui import TaskGUI

def main():
    """Haupt-Einstiegspunkt für CLI oder GUI."""
    init_db()

    if len(sys.argv) < 2:
        print("Willkommen im Task- und Zeiterfassungstool!")
        print("Nutze 'help' für eine Liste der verfügbaren Befehle.")
        print("Oder starte 'python main.py gui' für die GUI.\n")
        return

    command = sys.argv[1].lower()
    args = sys.argv[2:]  # weitere Argumente

    if command == "gui":
        # Starte die Tkinter-GUI
        app = TaskGUI()
        app.mainloop()
    else:
        # Command-Line-Modus
        line = " ".join(sys.argv[1:])
        handle_command(line, output_func=print)

if __name__ == "__main__":
    main()
