import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from commands import handle_command
import sys

class TaskGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Task Manager GUI")
        self.geometry("600x400")
        self.configure(bg="black")

        # Status für das Ein-/Ausklappen des Ausgabefeldes
        self.collapsed = False

        self.protocol("WM_DELETE_WINDOW", self.minimize_window)  # Schließen minimiert das Fenster

        self.output_box = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=20, bg="black", fg="#ffb347")
        self.output_box.pack(fill=tk.BOTH, expand=True)

        self.input_var = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=self.input_var, bg="black", fg="#ffb347", insertbackground="#ffb347")
        self.entry.bind("<Return>", self.execute_command)
        self.entry.pack(fill=tk.X)

        # Fokus auf Eingabefeld setzen
        self.entry.focus_set()
        self.bind("<FocusIn>", lambda event: self.entry.focus_set())

        self.print_line("Willkommen zur Task Manager GUI! Geben Sie einen Befehl ein.")

    def execute_command(self, event):
        command = self.input_var.get().strip()
        if command:
            self.print_line(f"> {command}")
            self.input_var.set("")
            if command.lower() == "collwin":
                self.toggle_collapse()
            elif command.lower() == "exit":
                self.close_application()
            else:
                handle_command(command, output_func=self.print_line)

    def print_line(self, text):
        # Automatisches Einblenden des Ausgabe-Feldes bei Fehlern
        keywords = ["fehler", "unbekannt", "abgebrochen", "existiert nicht", "läuft bereits"]
        if any(keyword in text.lower() for keyword in keywords):
            if self.collapsed:
                self.toggle_collapse(force_expand=True)

        self.output_box.insert(tk.END, text + "\n")
        self.output_box.see(tk.END)

    def toggle_collapse(self, force_expand=False):
        if force_expand:
            # Nur ausklappen, wenn eingeklappt
            if self.collapsed:
                self.output_box.pack(fill=tk.BOTH, expand=True)
                self.geometry("600x400")
                self.collapsed = False
            return

        if self.collapsed:
            # Wieder einblenden
            self.output_box.pack(fill=tk.BOTH, expand=True)
            self.geometry("600x400")
            self.collapsed = False
        else:
            # Ausblenden und Fenstergröße anpassen
            self.output_box.pack_forget()
            self.geometry("600x100")
            self.collapsed = True

    def minimize_window(self):
        """Minimiert das Fenster statt es zu schließen."""
        self.iconify()

    def close_application(self):
        """Beendet die Anwendung vollständig."""
        self.print_line("Programm wird beendet...")
        self.destroy()
        sys.exit(0)
