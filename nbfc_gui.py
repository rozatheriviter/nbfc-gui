#!/usr/bin/env python3

import tkinter as tk
import subprocess

def set_speed(value):
    # Automatically set the speed whenever the slider is adjusted.
    subprocess.run(["nbfc", "set", "-s", str(value)])

def set_auto():
    # Run automatic mode
    subprocess.run(["nbfc", "set", "-a"])

# Create the main window
root = tk.Tk()
root.title("NBFC Control")

# Create the slider bar for speed (0 to 100) with an automatic callback
scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL,
                 label="Set Speed", command=set_speed)
scale.pack(pady=10)

# Create and place the button for automatic mode
btn_set_auto = tk.Button(root, text="Set Automatic", command=set_auto, width=20)
btn_set_auto.pack(pady=10)

# Start the GUI event loop
root.mainloop()
