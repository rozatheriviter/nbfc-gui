#!/usr/bin/env python3
import tkinter as tk
import subprocess

def set_speed():
    # Get the current value from the slider and run the command with that speed
    speed = scale.get()
    subprocess.run(["nbfc", "set", "-s", str(speed)])

def set_auto():
    # Runs the command: nbfc set -a
    subprocess.run(["nbfc", "set", "-a"])

# Create the main window
root = tk.Tk()
root.title("NBFC Control")

# Create the slider bar for speed (0 to 100)
scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Set Speed")
scale.pack(pady=10)

# Create and place the buttons
btn_set_speed = tk.Button(root, text="Apply Speed", command=set_speed, width=20)
btn_set_speed.pack(pady=10)

btn_set_auto = tk.Button(root, text="Set Automatic", command=set_auto, width=20)
btn_set_auto.pack(pady=10)

# Start the GUI event loop
root.mainloop()
