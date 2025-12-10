#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import shutil
import time
import threading
import sys
import os
import venv

# --- Configuration & Constants ---
APP_TITLE = "Fan Control"
BG_COLOR = "#F5F5F7"  # Apple-like light gray
TEXT_COLOR = "#1D1D1F" # Nearly black
ACCENT_COLOR = "#007AFF" # Apple Blue
FONT_FAMILY = "Helvetica" # Fallback to Arial if needed
POLL_INTERVAL_MS = 2000

# --- Bootstrapping ---

REQUIREMENTS_FILE = "requirements.txt"
VENV_NAME = ".venv"

def get_base_prefix_compat():
    """Get base prefix, compatible with Python versions."""
    return getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None) or sys.prefix

def in_virtualenv():
    return get_base_prefix_compat() != sys.prefix

def ensure_venv():
    """Ensure the script is running in a virtual environment with satisfied requirements."""
    # If we are already in a venv, return
    if in_virtualenv():
        return

    # Path to venv
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(script_dir, VENV_NAME)

    # Python executable in venv
    if sys.platform == "win32":
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")

    # Create venv if not exists
    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment in {venv_dir}...")
        try:
            venv.create(venv_dir, with_pip=True)
        except Exception as e:
            print(f"Error creating venv: {e}")
            sys.exit(1)

    # Install requirements if requirements.txt exists
    req_path = os.path.join(script_dir, REQUIREMENTS_FILE)
    if os.path.exists(req_path):
        # Check if we should try installing.
        # For simplicity in this script, we just run pip install.
        # Pip handles "already satisfied" quickly.
        print("Checking dependencies...")
        try:
            subprocess.check_call([venv_python, "-m", "pip", "install", "-r", req_path], stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print("Failed to install dependencies.")
            sys.exit(1)

    # Re-launch script in venv
    print("Relaunching in virtual environment...")
    # Use os.execv to replace the current process
    try:
        os.execv(venv_python, [venv_python] + sys.argv)
    except OSError as e:
        print(f"Failed to relaunch in venv: {e}")
        sys.exit(1)

# Run bootstrapping before anything else
ensure_venv()

# --- NBFC Interface ---

class NBFCController:
    @staticmethod
    def is_installed():
        return shutil.which("nbfc") is not None

    @staticmethod
    def get_status():
        """
        Returns a dict with status info or None if error.
        Keys: 'service_enabled', 'read_only', 'config', 'temp', 'speed', 'speed_mode'
        """
        try:
            result = subprocess.run(["nbfc", "status", "-a"], capture_output=True, text=True, check=True)
            output = result.stdout
            status = {
                "config": None,
                "temp": "N/A",
                "speed": "N/A",
                "speed_mode": "Manual"
            }

            for line in output.splitlines():
                line = line.strip()
                if "Selected config name:" in line:
                    status["config"] = line.split(":", 1)[1].strip()
                elif "Temperature:" in line:
                    status["temp"] = line.split(":", 1)[1].strip()
                elif "Fan speed:" in line:
                    val = line.split(":", 1)[1].strip()
                    status["speed"] = val
                    if "(Auto)" in val:
                        status["speed_mode"] = "Auto"
                    else:
                        status["speed_mode"] = "Manual"
            return status
        except subprocess.CalledProcessError:
            return None
        except FileNotFoundError:
            return None

    @staticmethod
    def get_recommendations():
        try:
            result = subprocess.run(["nbfc", "config", "-r"], capture_output=True, text=True, check=True)
            configs = [line.strip() for line in result.stdout.splitlines() if line.strip()]
            return configs
        except subprocess.CalledProcessError:
            return []

    @staticmethod
    def apply_config(config_name):
        try:
            subprocess.run(["nbfc", "config", "-a", config_name], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def set_speed(value):
        try:
            subprocess.run(["nbfc", "set", "-s", str(int(value))], check=True)
        except subprocess.CalledProcessError:
            pass

    @staticmethod
    def set_auto():
        try:
            subprocess.run(["nbfc", "set", "-a"], check=True)
        except subprocess.CalledProcessError:
            pass

# --- UI Components ---

class StyledApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("400x500")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        # Configure Styles
        style = ttk.Style(self)
        style.theme_use('clam') # 'clam' usually allows more color customization than 'default'

        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=(FONT_FAMILY, 12))
        style.configure("Title.TLabel", font=(FONT_FAMILY, 24, "bold"))
        style.configure("Status.TLabel", font=(FONT_FAMILY, 48, "bold"))
        style.configure("SubStatus.TLabel", font=(FONT_FAMILY, 14), foreground="#86868B")

        style.configure("TButton",
                        font=(FONT_FAMILY, 11),
                        borderwidth=0,
                        background="white", # Default button bg
                        foreground=ACCENT_COLOR) # Text color

        # Custom button style for primary actions
        style.configure("Primary.TButton",
                        background=ACCENT_COLOR,
                        foreground="white",
                        font=(FONT_FAMILY, 12, "bold"),
                        padding=10)

        style.map("Primary.TButton",
                  background=[('active', "#0051A8")])

        # Initialize sequence
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        if not NBFCController.is_installed():
            self.show_install_screen()
        else:
            self.check_configuration()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_install_screen(self):
        self.clear_container()

        lbl_title = ttk.Label(self.container, text="NBFC Missing", style="Title.TLabel")
        lbl_title.pack(pady=(40, 20))

        lbl_msg = ttk.Label(self.container,
                            text="Notebook FanControl (nbfc) is not installed or not found in your PATH.\n\nPlease install it to use this application.",
                            wraplength=350, justify="center")
        lbl_msg.pack(pady=10)

        # In a real scenario, we might offer to install or open a browser.
        btn_quit = ttk.Button(self.container, text="Quit", command=self.destroy)
        btn_quit.pack(pady=40)

    def check_configuration(self):
        status = NBFCController.get_status()
        if status and status.get("config"):
            self.show_main_interface()
        else:
            self.show_setup_wizard()

    def show_setup_wizard(self):
        self.clear_container()

        lbl_title = ttk.Label(self.container, text="Welcome", style="Title.TLabel")
        lbl_title.pack(pady=(20, 10))

        lbl_intro = ttk.Label(self.container,
                              text="Let's configure your fan control profile.",
                              style="SubStatus.TLabel")
        lbl_intro.pack(pady=(0, 20))

        lbl_loading = ttk.Label(self.container, text="Fetching recommendations...", foreground="#86868B")
        lbl_loading.pack()

        self.update() # Force redraw

        configs = NBFCController.get_recommendations()
        lbl_loading.destroy()

        if not configs:
            configs = ["Generic", "HP", "Dell", "Lenovo", "Asus", "Acer"] # Fallbacks if detection fails

        lbl_select = ttk.Label(self.container, text="Select your model:")
        lbl_select.pack(anchor="w", pady=(10, 5))

        selected_config = tk.StringVar()
        combo = ttk.Combobox(self.container, textvariable=selected_config, values=configs, state="readonly")
        combo.pack(fill="x", pady=5)
        if configs:
            combo.current(0)

        def on_apply():
            cfg = selected_config.get()
            if cfg:
                if NBFCController.apply_config(cfg):
                    self.show_main_interface()
                else:
                    messagebox.showerror("Error", "Failed to apply configuration.")

        btn_apply = ttk.Button(self.container, text="Apply Configuration", style="Primary.TButton", command=on_apply)
        btn_apply.pack(pady=30, fill="x")

    def show_main_interface(self):
        self.clear_container()

        # Header
        header_frame = ttk.Frame(self.container)
        header_frame.pack(fill="x", pady=(0, 20))

        lbl_title = ttk.Label(header_frame, text="Fan Control", style="Title.TLabel")
        lbl_title.pack(side="left")

        # Status Display
        self.status_frame = ttk.Frame(self.container)
        self.status_frame.pack(fill="x", pady=20)

        self.lbl_temp = ttk.Label(self.status_frame, text="--°C", style="Status.TLabel")
        self.lbl_temp.pack()

        self.lbl_speed_text = ttk.Label(self.status_frame, text="Checking...", style="SubStatus.TLabel")
        self.lbl_speed_text.pack()

        # Controls
        control_frame = ttk.Frame(self.container)
        control_frame.pack(fill="x", pady=40)

        lbl_manual = ttk.Label(control_frame, text="Manual Speed")
        lbl_manual.pack(anchor="w", pady=(0, 5))

        self.slider_var = tk.DoubleVar()
        self.slider = tk.Scale(control_frame, from_=0, to=100, orient="horizontal",
                               variable=self.slider_var, showvalue=0,
                               bg=BG_COLOR, highlightthickness=0, bd=0, troughcolor="#E5E5EA", activebackground=ACCENT_COLOR)
        # Tkinter native scale looks better than ttk scale on some systems for customization,
        # but ttk.Scale is more "native". Let's stick to ttk.Scale if possible, but ttk.Scale doesn't support 'command'
        # as continuously as we might like or easy styling.
        # Let's use ttk.Scale
        self.slider = ttk.Scale(control_frame, from_=0, to=100, variable=self.slider_var, command=self.on_slider_drag)
        self.slider.pack(fill="x")
        # Update speed only on release to avoid subprocess spam
        self.slider.bind("<ButtonRelease-1>", self.on_slider_release)

        self.lbl_slider_val = ttk.Label(control_frame, text="0%", font=(FONT_FAMILY, 10))
        self.lbl_slider_val.pack(anchor="e")

        # Footer Actions
        footer_frame = ttk.Frame(self.container)
        footer_frame.pack(side="bottom", fill="x", pady=10)

        self.btn_auto = ttk.Button(footer_frame, text="Enable Auto", style="Primary.TButton", command=self.enable_auto)
        self.btn_auto.pack(fill="x")

        # Start polling
        self.update_status()

    def on_slider_drag(self, val):
        """Update label while dragging, but don't set speed yet."""
        val = int(float(val))
        self.lbl_slider_val.config(text=f"{val}%")

    def on_slider_release(self, event):
        """Set speed only when user releases the slider."""
        val = int(self.slider_var.get())
        NBFCController.set_speed(val)
        # When user touches slider, we are in manual mode
        self.btn_auto.configure(text="Enable Auto", style="Primary.TButton")

    def enable_auto(self):
        NBFCController.set_auto()
        self.btn_auto.configure(text="Auto Enabled", style="TButton") # Change style to indicate active/passive?
        # Maybe disable slider?
        # For Jony Ive simplicity, maybe just reset UI state.

    def update_status(self):
        status = NBFCController.get_status()
        if status:
            self.lbl_temp.config(text=f"{status.get('temp', '--')}")

            speed = status.get('speed', '0 %')
            mode = status.get('speed_mode', 'Manual')

            self.lbl_speed_text.config(text=f"{speed} · {mode}")

            # Update slider if in Auto mode to reflect reality?
            # Or keep slider as "User Request"?
            # Usually better not to move slider under user's finger.

            if mode == "Auto":
                self.btn_auto.configure(text="Auto Enabled", state="disabled")
            else:
                self.btn_auto.configure(text="Enable Auto", state="normal", style="Primary.TButton")

        self.after(POLL_INTERVAL_MS, self.update_status)

if __name__ == "__main__":
    app = StyledApp()
    app.mainloop()
