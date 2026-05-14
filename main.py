import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import time
import random
import json
import os
import ctypes
from pynput.keyboard import Listener, Key, KeyCode
from pynput.mouse import Controller as MouseController

# Windows API for hardware-level input
SendInput = ctypes.windll.user32.SendInput

PUL = ctypes.POINTER(ctypes.c_ulong)
class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union): _fields_ = [("mi", MouseInput)]
class Input(ctypes.Structure): _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]

# Constants for mouse events
MOUSEEVENTF_MOVE, MOUSEEVENTF_ABSOLUTE = 0x0001, 0x8000
MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0002, 0x0004
MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP = 0x0008, 0x0010
MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP = 0x0020, 0x0040

# --- MODERN THEME SETTINGS ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AutoClickerV2(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.running = False
        self.program_running = True
        self.click_count = 0
        self.last_ui_update = 0
        self.profile_path = "profiles.json"
        self.mouse_controller = MouseController()
        
        self.settings = {
            "interval": 100, "random_range": 0, "hold_duration": 10,
            "button": "Left", "click_type": "Single", "click_limit": 0,
            "hotkey": "F8", "always_on_top": False,
            "target_mode": "Current Location", "target_x": 0, "target_y": 0, "area_random": 0
        }
        
        self.current_hotkey = Key.f8
        self.load_settings()
        
        self.title("AutoC v2.0")
        self.resizable(False, False)
        
        self.setup_ui()
        self.apply_settings_to_ui()
        
        # Threads
        threading.Thread(target=self.clicker_loop, daemon=True).start()
        threading.Thread(target=self.cursor_tracker_loop, daemon=True).start()
        
        self.listener_thread = Listener(on_press=self.on_press)
        self.listener_thread.start()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        # Menu Bar for Profiles
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Profile", command=self.save_settings)
        file_menu.add_command(label="Load Profile", command=self.load_settings_and_update)

        # Main Frame with Padding
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        def add_row(parent, label_text, widget, row):
            ctk.CTkLabel(parent, text=label_text, width=130, anchor="e").grid(row=row, column=0, sticky="e", padx=(10, 10), pady=5)
            widget.grid(row=row, column=1, sticky="w", padx=(0, 10), pady=5)

        # --- Group 1: Click Options ---
        group_click = ctk.CTkFrame(main_frame)
        group_click.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(group_click, text="Click Options", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=(10, 5), padx=15, sticky="w")

        self.hotkey_btn = ctk.CTkButton(group_click, text=self.settings["hotkey"], command=self.capture_hotkey, width=140, fg_color="#C62828", hover_color="#B71C1C")
        add_row(group_click, "Start Hotkey:", self.hotkey_btn, 1)

        self.button_var = ctk.StringVar(value=self.settings["button"])
        btn_menu = ctk.CTkOptionMenu(group_click, variable=self.button_var, values=["Left", "Right", "Middle"], width=140)
        add_row(group_click, "Mouse Button:", btn_menu, 2)

        self.click_type_var = ctk.StringVar(value=self.settings["click_type"])
        type_menu = ctk.CTkOptionMenu(group_click, variable=self.click_type_var, values=["Single", "Double", "Triple"], width=140)
        add_row(group_click, "Click Type:", type_menu, 3)

        self.limit_var = ctk.StringVar(value=str(self.settings["click_limit"]))
        add_row(group_click, "Click Limit:", ctk.CTkEntry(group_click, textvariable=self.limit_var, width=140), 4)
        ctk.CTkLabel(group_click, text="", height=5).grid(row=5, column=0) # Spacer

        # --- Group 2: Delay Settings ---
        group_delay = ctk.CTkFrame(main_frame)
        group_delay.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(group_delay, text="Delay Settings", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=(10, 5), padx=15, sticky="w")

        self.interval_var = ctk.StringVar(value=str(self.settings["interval"]))
        add_row(group_delay, "Interval (ms):", ctk.CTkEntry(group_delay, textvariable=self.interval_var, width=140), 1)

        self.random_var = ctk.StringVar(value=str(self.settings["random_range"]))
        add_row(group_delay, "Random (±ms):", ctk.CTkEntry(group_delay, textvariable=self.random_var, width=140), 2)

        self.hold_var = ctk.StringVar(value=str(self.settings["hold_duration"]))
        add_row(group_delay, "Hold (ms):", ctk.CTkEntry(group_delay, textvariable=self.hold_var, width=140), 3)
        ctk.CTkLabel(group_delay, text="", height=5).grid(row=4, column=0) # Spacer

        # --- Group 3: Targeting ---
        group_target = ctk.CTkFrame(main_frame)
        group_target.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(group_target, text="Targeting", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5), padx=15)

        self.target_mode_var = ctk.StringVar(value=self.settings["target_mode"])
        mode_frame = ctk.CTkFrame(group_target, fg_color="transparent")
        mode_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkRadioButton(mode_frame, text="Current Cursor", variable=self.target_mode_var, value="Current Location").pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(mode_frame, text="Fixed Location", variable=self.target_mode_var, value="Fixed Location").pack(side="left")

        coord_frame = ctk.CTkFrame(group_target, fg_color="transparent")
        coord_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(coord_frame, text="X:").pack(side="left")
        self.x_var = ctk.StringVar(value=str(self.settings["target_x"]))
        self.x_entry = ctk.CTkEntry(coord_frame, textvariable=self.x_var, width=60)
        self.x_entry.pack(side="left", padx=(5, 15))
        
        ctk.CTkLabel(coord_frame, text="Y:").pack(side="left")
        self.y_var = ctk.StringVar(value=str(self.settings["target_y"]))
        self.y_entry = ctk.CTkEntry(coord_frame, textvariable=self.y_var, width=60)
        self.y_entry.pack(side="left", padx=(5, 15))
        
        ctk.CTkButton(coord_frame, text="Pick Location", width=100, command=self.pick_location).pack(side="left")

        area_frame = ctk.CTkFrame(group_target, fg_color="transparent")
        area_frame.pack(fill="x", padx=15, pady=(0, 15))
        ctk.CTkLabel(area_frame, text="Area Random (px):").pack(side="left", padx=(0, 10))
        self.area_var = ctk.StringVar(value=str(self.settings["area_random"]))
        ctk.CTkEntry(area_frame, textvariable=self.area_var, width=60).pack(side="left")

        # --- Switches ---
        self.ontop_var = tk.BooleanVar(value=self.settings["always_on_top"])
        ctk.CTkSwitch(main_frame, text="Always on Top", variable=self.ontop_var, command=self.toggle_ontop).pack(anchor="w", padx=10)

        # --- Status Bar ---
        status_frame = ctk.CTkFrame(self, height=35, corner_radius=0)
        status_frame.pack(fill="x", side="bottom")
        
        self.status_var = ctk.StringVar(value="Status: Stopped")
        self.status_label = ctk.CTkLabel(status_frame, textvariable=self.status_var, font=ctk.CTkFont(weight="bold"), text_color="gray")
        self.status_label.pack(side="left", padx=20)
        
        self.count_var = ctk.StringVar(value="Clicks: 0")
        ctk.CTkLabel(status_frame, textvariable=self.count_var).pack(side="right", padx=20)

    def cursor_tracker_loop(self):
        while self.program_running:
            if self.target_mode_var.get() == "Current Location":
                pos = self.mouse_controller.position
                self.x_var.set(str(int(pos[0])))
                self.y_var.set(str(int(pos[1])))
                # Disable entry fields while tracking
                self.x_entry.configure(state="disabled")
                self.y_entry.configure(state="disabled")
            else:
                self.x_entry.configure(state="normal")
                self.y_entry.configure(state="normal")
            time.sleep(0.05)

    def toggle_ontop(self):
        self.attributes('-topmost', self.ontop_var.get())

    def capture_hotkey(self):
        self.is_capturing_hotkey = True
        self.hotkey_btn.configure(text="Press any key...")

    def on_press(self, key):
        if self.is_capturing_hotkey:
            self.current_hotkey = key
            name = getattr(key, 'name', getattr(key, 'char', str(key).replace("'", ""))).upper()
            self.after(0, lambda: self.hotkey_btn.configure(text=name))
            self.is_capturing_hotkey = False
            return
        if key == self.current_hotkey:
            self.toggle_clicking()

    def toggle_clicking(self):
        if not self.running:
            if not self.update_settings_from_ui(): return
            self.click_count = 0
            self.count_var.set("Clicks: 0")
        self.running = not self.running
        status, color = ("Running", "#4CAF50") if self.running else ("Stopped", "gray")
        self.after(0, lambda: self.status_var.set(f"Status: {status}"))
        self.after(0, lambda: self.status_label.configure(text_color=color))

    def update_settings_from_ui(self):
        try:
            self.settings.update({
                "interval": float(self.interval_var.get()),
                "random_range": float(self.random_var.get()),
                "hold_duration": float(self.hold_var.get()),
                "button": self.button_var.get(),
                "click_type": self.click_type_var.get(),
                "click_limit": int(self.limit_var.get()),
                "hotkey": self.hotkey_btn.cget("text"),
                "always_on_top": self.ontop_var.get(),
                "target_mode": self.target_mode_var.get(),
                "target_x": int(self.x_var.get()),
                "target_y": int(self.y_var.get()),
                "area_random": int(self.area_var.get())
            })
            return True
        except:
            messagebox.showerror("Invalid Input", "Please check all numeric fields.")
            return False

    def apply_settings_to_ui(self):
        self.attributes('-topmost', self.settings["always_on_top"])

    def save_settings(self):
        if self.update_settings_from_ui():
            with open(self.profile_path, 'w') as f: json.dump(self.settings, f)
            messagebox.showinfo("Success", "Settings saved.")

    def load_settings(self):
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, 'r') as f: self.settings.update(json.load(f))
            except: pass
        hk = self.settings["hotkey"]
        try:
            if hasattr(Key, hk.lower()): self.current_hotkey = getattr(Key, hk.lower())
            elif len(hk) == 1: self.current_hotkey = KeyCode.from_char(hk.lower())
            else: self.current_hotkey = Key.f8
        except: self.current_hotkey = Key.f8

    def load_settings_and_update(self):
        self.load_settings()
        self.interval_var.set(str(self.settings["interval"]))
        self.random_var.set(str(self.settings["random_range"]))
        self.hold_var.set(str(self.settings["hold_duration"]))
        self.button_var.set(self.settings["button"])
        self.click_type_var.set(self.settings["click_type"])
        self.limit_var.set(str(self.settings["click_limit"]))
        self.hotkey_btn.configure(text=self.settings["hotkey"])
        self.ontop_var.set(self.settings["always_on_top"])
        self.target_mode_var.set(self.settings["target_mode"])
        self.x_var.set(str(self.settings["target_x"]))
        self.y_var.set(str(self.settings["target_y"]))
        self.area_var.set(str(self.settings["area_random"]))
        self.toggle_ontop()

    def pick_location(self):
        self.overlay = ctk.CTkToplevel(self)
        self.overlay.attributes('-fullscreen', True, '-alpha', 0.3, '-topmost', True)
        self.overlay.configure(cursor="cross")
        ctk.CTkLabel(self.overlay, text="Click to pick coordinates (ESC to cancel)", font=ctk.CTkFont(size=20)).pack(expand=True)
        self.overlay.bind("<Button-1>", lambda e: (self.x_var.set(str(e.x_root)), self.y_var.set(str(e.y_root)), self.overlay.destroy()))
        self.overlay.bind("<Escape>", lambda e: self.overlay.destroy())

    def mouse_event(self, flags, x=0, y=0, data=0):
        if flags & MOUSEEVENTF_ABSOLUTE:
            x = int(x * 65535 / ctypes.windll.user32.GetSystemMetrics(0))
            y = int(y * 65535 / ctypes.windll.user32.GetSystemMetrics(1))
        ii_ = Input_I()
        ii_.mi = MouseInput(x, y, data, flags, 0, ctypes.pointer(ctypes.c_ulong(0)))
        ctypes.windll.user32.SendInput(1, ctypes.pointer(Input(ctypes.c_ulong(0), ii_)), ctypes.sizeof(Input))

    def perform_click(self):
        if self.settings["target_mode"] == "Fixed Location":
            tx = self.settings["target_x"] + (random.randint(-self.settings["area_random"], self.settings["area_random"]) if self.settings["area_random"] > 0 else 0)
            ty = self.settings["target_y"] + (random.randint(-self.settings["area_random"], self.settings["area_random"]) if self.settings["area_random"] > 0 else 0)
            self.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, tx, ty)
        btn = self.settings["button"]
        down = MOUSEEVENTF_LEFTDOWN if btn == "Left" else MOUSEEVENTF_RIGHTDOWN if btn == "Right" else MOUSEEVENTF_MIDDLEDOWN
        up = MOUSEEVENTF_LEFTUP if btn == "Left" else MOUSEEVENTF_RIGHTUP if btn == "Right" else MOUSEEVENTF_MIDDLEUP
        clicks = 1 if self.settings["click_type"] == "Single" else 2 if self.settings["click_type"] == "Double" else 3
        for _ in range(clicks):
            self.mouse_event(down)
            time.sleep(self.settings["hold_duration"] / 1000.0)
            self.mouse_event(up)
            if clicks > 1: time.sleep(0.05)
        self.click_count += 1
        curr = time.time()
        if curr - self.last_ui_update > 0.1:
            self.last_ui_update = curr
            self.after(0, lambda c=self.click_count: self.count_var.set(f"Clicks: {c}"))

    def clicker_loop(self):
        while self.program_running:
            if self.running:
                if self.settings["click_limit"] > 0 and self.click_count >= self.settings["click_limit"]:
                    self.toggle_clicking()
                    self.after(0, lambda: self.count_var.set(f"Clicks: {self.click_count}"))
                    continue
                self.perform_click()
                interval = self.settings["interval"] + (random.uniform(-self.settings["random_range"], self.settings["random_range"]) if self.settings["random_range"] > 0 else 0)
                time.sleep(max(0.001, interval / 1000.0))
            else: time.sleep(0.1)

    def on_closing(self):
        self.program_running = False
        self.running = False
        self.destroy()

if __name__ == "__main__":
    app = AutoClickerV2()
    app.mainloop()
