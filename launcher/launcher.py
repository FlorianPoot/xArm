from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *

from lib.cartesian import *

import threading
import subprocess
import sys
import os
import time
import hid
import struct


FRAME_HEADER = 0x55
CMD_SERVO_MOVE = 0x03
CMD_MULT_SERVO_UNLOAD = 0x14
CMD_MULT_SERVO_POS_READ = 0x15

RASPBERRY_PI = sys.platform == "linux"
# sys.stderr = open("error_log.txt", "a")


class Launcher(Tk):

    def __init__(self):

        """Launcher window that launch selected app"""

        super(Launcher, self).__init__()

        self.device = hid.device()

        self.process = None
        self.joints_pos = [IntVar() for _ in range(6)]
        self.points_pos = [IntVar() for _ in range(3)]
        self.exit_joints_loop = False
        self.stop_pressed = False

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
        # self.listbox.grid(column=0, row=1, rowspan=3, padx=10, pady=10, sticky=N+S+E+W)

        self.update_apps_list()
        self.listbox.select_set(0)

        self.joints_frame = Frame(self, padx=5, pady=5, highlightthickness=1, highlightbackground="black")
        self.points_frame = Frame(self, padx=5, pady=5, highlightthickness=1, highlightbackground="black")

        if RASPBERRY_PI:
            start_image = PhotoImage(file="xArm/launcher/images/start.png")
            stop_image = PhotoImage(file="xArm/launcher/images/stop.png")
            joints_image = PhotoImage(file="xArm/launcher/images/joints.png")
        else:
            start_image = PhotoImage(file="images/start.png")
            stop_image = PhotoImage(file="images/stop.png")
            joints_image = PhotoImage(file="images/joints.png")

        self.start_button = ttk.Button(self, text="START", image=start_image, compound=TOP, command=self.start, takefocus=0, state=NORMAL)
        # self.start_button.grid(column=1, row=1, padx=(0, 10), pady=5)

        self.stop_button = ttk.Button(self, text="STOP", image=stop_image, compound=TOP, command=self.stop, takefocus=0, state=DISABLED)
        # self.stop_button.grid(column=1, row=2, padx=(0, 10), pady=5)

        self.joints_button = ttk.Button(self, text="JOINTS", image=joints_image, compound=TOP, command=self.joints_menu, takefocus=0)
        # self.joints_button.grid(column=1, row=3, padx=(0, 10), pady=5)

        self.back_button = ttk.Button(self, text="BACK", command=self.exit_joints_menu, takefocus=0)

        self.main_menu()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.mainloop()

    def update_apps_list(self):

        selected = self.listbox.curselection()
        if len(selected) < 1:
            selected = (0, )

        # Clear all items
        self.listbox.delete(0, END)

        for app in os.listdir("xArm/apps" if RASPBERRY_PI else "../apps"):
            self.listbox.insert(END, app)

        self.listbox.select_set(selected[0])

        # Refresh every 5 seconds
        self.listbox.after(5000, self.update_apps_list)

    def main_menu(self):

        self.listbox.grid(column=0, row=1, rowspan=3, padx=10, pady=10, sticky=N+S+E+W)
        self.start_button.grid(column=1, row=1, padx=(0, 10), pady=5)
        self.stop_button.grid(column=1, row=2, padx=(0, 10), pady=5)
        self.joints_button.grid(column=1, row=3, padx=(0, 10), pady=5)

    def joints_menu(self):

        # Clear window
        self.listbox.grid_forget()
        self.start_button.grid_forget()
        self.stop_button.grid_forget()
        self.joints_button.grid_forget()

        for joint in range(6):
            f = Frame(self.joints_frame)
            Label(f, text=f"Joint {joint + 1}: ", font="Arial 12").grid(column=0, row=0, sticky=N+S+E+W)
            Label(f, textvariable=self.joints_pos[joint], font="Arial 15", relief=GROOVE, padx=5, pady=5).grid(column=1, row=0, sticky=N+S+E+W)
            f.grid(column=joint % 3, row=joint // 3, padx=10, pady=10)

            self.joints_frame.columnconfigure(joint % 3, weight=1)
            self.joints_frame.rowconfigure(joint // 3, weight=1)

        self.joints_frame.grid(column=0, row=1, padx=40, pady=(0, 10), sticky=N+S+E+W)

        axis = ("X", "Y", "Z")
        for point in range(3):
            f = Frame(self.points_frame)
            Label(f, text=f"{axis[point]}: ", font="Arial 12").grid(column=0, row=0, sticky=N+S+E+W)
            Label(f, textvariable=self.points_pos[point], font="Arial 15", relief=GROOVE, padx=5, pady=5).grid(column=1, row=0, sticky=N+S+E+W)
            f.grid(column=point, row=0, padx=10, pady=10)

            self.points_frame.columnconfigure(point, weight=1)
            self.points_frame.rowconfigure(0, weight=1)

        self.points_frame.grid(column=0, row=2, padx=80, pady=(10, 0), sticky=N+S+E+W)

        self.back_button.grid(column=0, row=3, pady=15)

        # Connect to xArm
        try:
            self.device.open(0x0483, 0x5750)  # LOBOT VendorID/ProductID
        except OSError:
            showerror("Error", "Unable to connect to xArm (open failed)")
        else:
            print(f"Manufacturer: {self.device.get_manufacturer_string()}")
            print(f"Product: {self.device.get_product_string()}")
            print(f"Serial No: {self.device.get_serial_number_string()}")

            self.exit_joints_loop = False
            threading.Thread(target=self.get_joints_pos, daemon=True).start()

    def exit_joints_menu(self):

        self.exit_joints_loop = True

        self.device.close()

        self.joints_frame.grid_forget()
        self.points_frame.grid_forget()
        self.back_button.grid_forget()

        self.main_menu()

    def get_joints_pos(self):

        while not self.exit_joints_loop:
            buf = bytearray(12)

            buf[0] = 0x00  # Hid id
            buf[1] = FRAME_HEADER
            buf[2] = FRAME_HEADER
            buf[3] = 9
            buf[4] = CMD_MULT_SERVO_POS_READ
            buf[5] = 6

            for index, servo in enumerate((6, 5, 4, 3, 2, 1)):
                buf[6 + index] = servo

            self.device.write(buf)
            time.sleep(0.2)

            data = bytearray(self.device.read(64))
            if data[:2] != b"\x55\x55" or data is None:
                raise ValueError("data don't match with what excepted")

            positions = list()
            for i in range(6):
                pos = data[5 + (i * 3):8 + (i * 3)]
                pos = struct.unpack("<H", pos[1:])

                positions.append(pos[0])

            for joint, pos in zip(self.joints_pos, positions):
                joint.set(pos)

            points = compute_fk(tuple(positions))
            for point, pos in zip(self.points_pos, points):
                point.set(pos)

            # Refresh rate
            time.sleep(1)

    def start(self):
        if RASPBERRY_PI:
            self.event_generate("<Motion>", warp=True, x=0, y=0)

        if len(self.listbox.curselection()) > 0:
            threading.Thread(target=self.running, daemon=True).start()

            self.start_button.config(state=DISABLED)
            self.stop_button.config(state=NORMAL)
            self.joints_button.config(state=DISABLED)

            self.state_label.config(text="RUNNING", fg="green")
        else:
            showwarning("Select", "Please select an application from the list")

    def stop(self):
        if RASPBERRY_PI:
            self.event_generate("<Motion>", warp=True, x=0, y=0)

        self.process.terminate()
        self.stop_pressed = True

    def running(self):

        selected_app = self.listbox.get(self.listbox.curselection())
        self.process = subprocess.Popen([sys.executable, f"xArm/apps/{selected_app}/main.py" if RASPBERRY_PI else f"../apps/{selected_app}/main.py"])
        self.process.wait()

        self.stop_button.config(state=DISABLED)

        if self.process.returncode == 0:
            # showinfo("Done", "The application has finished running")
            self.state_label.config(text="DONE", fg="blue")
            time.sleep(2)
        elif self.stop_pressed:
            self.state_label.config(text="STOPPED", fg="yellow")
            time.sleep(2)
        else:
            # showerror("Error", "An error occured")
            self.state_label.config(text="ERROR", fg="red")

            for i in range(24):
                bg = self.state_label.cget("background")
                fg = self.state_label.cget("foreground")
                self.state_label.configure(background=fg, foreground=bg)
                time.sleep(0.5)

        self.stop_pressed = False
        self.state_label.config(text="IDLE", fg="grey")
        self.start_button.config(state=NORMAL)
        self.joints_button.config(state=NORMAL)


if __name__ == "__main__":
    Launcher()
