# gui.py / python3.7 and higher
import sys
import tkinter as tk
import tkinter.scrolledtext as scrolledtext

from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

from commands import handle_command
from db import list_tasks, start_task, stop_task, delete_task


class TaskGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Task - Zeiterfassung GUI")
        self.geometry("600x400")
        self.configure(bg="black")

        # Status für das Ein-/Ausklappen des Ausgabefeldes
        self.collapsed = False

        # Temporäre Löschanfrage (GUI-Sicherheitsabfrage)
        self.pending_delete = None

        # Tray-Icon-Objekt und -Status
        self.tray_icon = None
        self.tray_icon_initialized = False

        # Beim Schließen des Fensters -> in die Tray minimieren
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        # Ausgabe-Box (ScrolledText)
        self.output_box = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, height=20, bg="black", fg="#ffb347"
        )
        self.output_box.pack(fill=tk.BOTH, expand=True)

        # Eingabe-Zeile
        self.input_var = tk.StringVar()
        self.entry = tk.Entry(
            self,
            textvariable=self.input_var,
            bg="black",
            fg="#ffb347",
            insertbackground="#ffb347",
        )
        self.entry.bind("<Return>", self.execute_command)
        self.entry.pack(fill=tk.X)

        # Fokus direkt auf das Eingabefeld
        self.entry.focus_set()
        self.bind("<FocusIn>", lambda event: self.entry.focus_set())

        # Begrüßung
        self.print_line("Willkommen zur Task Manager GUI! Geben Sie einen Befehl ein.")

    def execute_command(self, event=None):
        command = self.input_var.get().strip()
        if not command:
            return

        self.print_line(f"> {command}")
        self.input_var.set("")

        # Wenn eine Löschanfrage aussteht
        if self.pending_delete:
            if command.lower() in ["y", "yes"]:
                taskname = self.pending_delete
                self.pending_delete = None
                # Jetzt wird wirklich gelöscht - ohne weitere Abfrage
                delete_task(taskname, output_func=self.print_line, is_gui=False)
            elif command.lower() in ["n", "no"]:
                self.print_line("Löschen abgebrochen.")
                self.pending_delete = None
            else:
                self.print_line("Bitte antworte mit 'y' (ja) oder 'n' (nein).")
            return

        # Normale Befehlsverarbeitung
        cmd_lower = command.lower()
        if cmd_lower.startswith("delete"):
            parts = command.split(" ", 1)
            if len(parts) > 1 and parts[1]:
                taskname = parts[1]
                self.pending_delete = taskname
                self.print_line(f"Willst du den Task '{taskname}' wirklich löschen? (y/n):")
            else:
                self.print_line("Syntax: delete <taskname>")

        elif cmd_lower == "collwin":
            self.toggle_collapse()

        elif cmd_lower == "exit":
            self.close_application()

        else:
            # Alle anderen Befehle an handle_command
            handle_command(command, output_func=self.print_line)

    def print_line(self, text: str):
        """Schreibt Text ans Ende des ScrolledText."""
        self.output_box.insert(tk.END, text + "\n")
        self.output_box.see(tk.END)

    def toggle_collapse(self):
        """Klappt die Ausgabe-Box ein oder aus."""
        if self.collapsed:
            self.output_box.pack(fill=tk.BOTH, expand=True)
            self.geometry("600x400")
            self.collapsed = False
        else:
            self.output_box.pack_forget()
            self.geometry("600x25")
            self.collapsed = True

    def minimize_to_tray(self):
        """Minimiert das Fenster in die System-Tray."""
        self.withdraw()
        if not self.tray_icon_initialized:
            self.tray_icon = Icon(
                "TaskManager",
                self.create_tray_icon(),
                menu=self.create_tray_menu()
            )
            self.tray_icon.run_detached()
            self.tray_icon_initialized = True
        else:
            self.update_tray_menu()

    def create_tray_icon(self):
        """Erzeugt ein einfaches Icon (64x64) mit 'T'."""
        image = Image.new("RGB", (64, 64), color="white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 64, 64), fill="black", outline="white")
        draw.text((16, 20), "T", fill="white")
        return image

    def create_tray_menu(self):
        """
        Erzeugt das System-Tray-Menü dynamisch.

        Für jeden Task gibt es einen Menüpunkt, der per Klick
        dessen Status togglen (Start/Stop) kann.
        """
        tasks = self.get_tasks()
        menu_items = []

        # Wir schreiben eine kleine 'Factory'-Funktion, die (icon, item) entgegennimmt.
        def make_tray_callback(task_name):
            """Erzeugt einen Callback (icon, item) -> toggelt 'task_name'."""
            def tray_callback(icon, item):
                self._toggle_task(task_name)
            return tray_callback

        for name, is_running, _ in tasks:
            prefix = "✓ " if is_running else ""
            menu_items.append(
                MenuItem(
                    f"{prefix}{name}",
                    make_tray_callback(name)  # der Callback weiß, welchen Task er togglen soll
                )
            )

        # Zusätzliche Einträge
        menu_items.append(MenuItem("Öffnen", self._open_callback))

        return Menu(*menu_items)

    def _toggle_task(self, task_name):
        """Startet oder stoppt den Task (task_name) abhängig vom aktuellen Status."""
        tasks = self.get_tasks()
        for (tname, is_running, _) in tasks:
            if tname == task_name:
                if is_running:
                    stop_task(task_name, output_func=self.print_line)
                else:
                    start_task(task_name, output_func=self.print_line)
                break
        self.update_tray_menu()

    def _open_callback(self, icon, item):
        """Callback zum Öffnen (aus dem Tray)."""
        self.show_window()

    def _quit_callback(self, icon, item):
        """Callback zum kompletten Beenden."""
        self.close_application()

    def update_tray_menu(self):
        """Aktualisiert das Tray-Menü (z. B. nach Start/Stop)."""
        if self.tray_icon:
            self.tray_icon.menu = self.create_tray_menu()
            self.tray_icon.update_menu()

    def get_tasks(self):
        """
        Fragt list_tasks() ab und parst das Ergebnis.

        Erwartetes Format je Zeile:
          Task: <Name>, Status: läuft/inaktiv, Mindest-Minuten: <Zahl>
        """
        lines = []

        def collector(line):
            lines.append(line)

        list_tasks(output_func=collector)

        if not lines:
            return []

        parsed_tasks = []
        for task_info in lines:
            # task_info sollte aussehen wie: "Task: foo, Status: läuft, Mindest-Minuten: 10"
            try:
                parts = task_info.split(", ")
                name = parts[0].split(": ")[1]
                is_running = (parts[1].split(": ")[1] == "läuft")
                min_minutes = int(parts[2].split(": ")[1])
                parsed_tasks.append((name, is_running, min_minutes))
            except (IndexError, ValueError) as e:
                self.print_line(f"Fehler beim Parsen: {task_info} ({e})")

        return parsed_tasks

    def show_window(self):
        """Zeigt das Fenster wieder an (aus der Tray-Ansicht)."""
        if self.tray_icon_initialized and self.tray_icon:
            self.tray_icon.stop()
        self.tray_icon_initialized = False
        self.deiconify()
        self.update()

    def close_application(self):
        """Beendet die Anwendung vollständig."""
        if self.tray_icon_initialized and self.tray_icon:
            self.tray_icon.stop()
        self.destroy()
        sys.exit(0)
