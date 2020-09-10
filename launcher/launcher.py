from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *

import threading
import subprocess
import sys
import os
import time


RASPBERRY_PI = sys.platform == "linux"


class Launcher(Tk):

    def __init__(self):

        """Launcher window that launch selected app"""

        super(Launcher, self).__init__()

        self.process = None
        self.apps = list()

        self.title("xArm Launcher")

        if RASPBERRY_PI:
            self.configure(cursor="none")
            self.geometry("480x320+0+0")
            self.overrideredirect(True)
        else:
            self.geometry("480x320")

        self.resizable(False, False)
        self.focus_set()

        self.title_frame = Frame(self)

        self.title_label = Label(self.title_frame, text="xArm Launcher -", font="Arial 15")
        self.title_label.pack(side=LEFT)

        self.state_label = Label(self.title_frame, text="IDLE", font="Arial 15 bold", fg="grey")
        self.state_label.pack(side=RIGHT)

        self.title_frame.grid(column=0, row=0, columnspan=2, pady=10)

        self.listbox = Listbox(self, selectmode=BROWSE, font="Arial 18", activestyle="none")
        self.listbox.grid(column=0, row=1, rowspan=3, padx=10, pady=10, sticky=N+S+E+W)

        for app in os.listdir("xArm/apps" if RASPBERRY_PI else "../apps"):
            self.apps.append(app)
            self.listbox.insert(END, app)

        self.listbox.select_set(0)

        if RASPBERRY_PI:
            start_image = PhotoImage(file="xArm/launcher/images/start.png")
            stop_image = PhotoImage(file="xArm/launcher/images/stop.png")
            joints_image = PhotoImage(file="xArm/launcher/images/joints.png")
        else:
            start_image = PhotoImage(file="images/start.png")
            stop_image = PhotoImage(file="images/stop.png")
            joints_image = PhotoImage(file="images/joints.png")

        self.start_button = ttk.Button(self, text="START", image=start_image, compound=TOP, command=self.start, takefocus=0, state=NORMAL)
        self.start_button.grid(column=1, row=1, padx=10, pady=5)

        self.stop_button = ttk.Button(self, text="STOP", image=stop_image, compound=TOP, command=self.stop, takefocus=0, state=DISABLED)
        self.stop_button.grid(column=1, row=2, padx=10, pady=5)

        ttk.Button(self, text="JOINTS", image=joints_image, compound=TOP, command=None, takefocus=0).grid(column=1, row=3, padx=10, pady=5)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.mainloop()

    def start(self):
        if RASPBERRY_PI:
            self.event_generate("<Motion>", warp=True, x=0, y=0)

        if len(self.listbox.curselection()) > 0:
            threading.Thread(target=self.running, daemon=True).start()

            self.start_button.config(state=DISABLED)
            self.stop_button.config(state=NORMAL)

            self.state_label.config(text="RUNNING", fg="green")
        else:
            showwarning("Select", "Please select an application from the list")

    def stop(self):
        if RASPBERRY_PI:
            self.event_generate("<Motion>", warp=True, x=0, y=0)

        self.process.terminate()

    def running(self):

        selected_app = self.listbox.get(self.listbox.curselection())
        self.process = subprocess.Popen([sys.executable, f"xArm/apps/{selected_app}/main.py" if RASPBERRY_PI else f"../apps/{selected_app}/main.py"])
        self.process.wait()

        self.stop_button.config(state=DISABLED)

        if self.process.returncode == 0:
            # showinfo("Done", "The application has finished running")
            self.state_label.config(text="DONE", fg="blue")
            time.sleep(2)
        else:
            # showerror("Error", "An error occured")
            self.state_label.config(text="ERROR", fg="red")

            for i in range(24):
                bg = self.state_label.cget("background")
                fg = self.state_label.cget("foreground")
                self.state_label.configure(background=fg, foreground=bg)
                time.sleep(0.5)

        self.state_label.config(text="IDLE", fg="grey")
        self.start_button.config(state=NORMAL)


if __name__ == "__main__":
    Launcher()
