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

def update_entry(val):
    # Update the text entry with the slider's value
    entry_speed.delete(0, tk.END)
    entry_speed.insert(0, str(val))

def update_slider(event):
    # Update the slider if the entry is changed and Enter is pressed
    try:
        new_val = int(entry_speed.get())
        if 0 <= new_val <= 100:
            scale.set(new_val)
    except ValueError:
        # Ignore invalid input
        pass

# Create the main window
root = tk.Tk()
root.title("NBFC Control")

# Create the slider bar for speed (0 to 100) with a command callback to update the entry
scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Set Speed", command=update_entry)
scale.pack(pady=10)

# Create a text entry widget that shows the current speed value
entry_speed = tk.Entry(root, width=5)
entry_speed.pack(pady=5)
entry_speed.bind("<Return>", update_slider)

# Set initial value of the entry to match the slider
entry_speed.insert(0, str(scale.get()))

# Create and place the buttons
btn_set_speed = tk.Button(root, text="Apply Speed", command=set_speed, width=20)
btn_set_speed.pack(pady=10)

btn_set_auto = tk.Button(root, text="Set Automatic", command=set_auto, width=20)
btn_set_auto.pack(pady=10)

# Start the GUI event loop
root.mainloop()
