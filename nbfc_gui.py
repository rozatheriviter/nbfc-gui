#!/usr/bin/env python3

import tkinter as tk
import subprocess

# Function to set the speed via nbfc
def set_speed(value):
    subprocess.run(["nbfc", "set", "-s", str(value)])

# Function to run automatic mode
def set_auto():
    subprocess.run(["nbfc", "set", "-a"])

# Initialize main window with dark background
root = tk.Tk()
root.title("NBFC Control")
root.configure(bg="#2e2e2e")  # Dark background

# Dark-themed styling options
label_fg = "#ffffff"      # White text for labels
button_bg = "#444444"     # Darker button background
button_fg = "#ffffff"     # White text on buttons
scale_bg = "#2e2e2e"       # Same as window background
scale_trough = "#555555"  # Slightly lighter for the slider trough

# Create the slider for speed with dark mode styling
scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL,
                 label="Set Speed", command=set_speed,
                 bg=scale_bg, fg=label_fg, highlightbackground=scale_bg,
                 troughcolor=scale_trough)
scale.pack(pady=10)

# Create a dark-themed button for automatic mode
btn_set_auto = tk.Button(root, text="Set Automatic", command=set_auto,
                         bg=button_bg, fg=button_fg, activebackground="#666666",
                         activeforeground=button_fg, width=20)
btn_set_auto.pack(pady=10)

# ----- Nyan Cat Animation -----
# Load all frames from the animated nyancat.gif
frames = []
frame_index = 0
try:
    # Load frames until an exception is raised (no more frames)
    while True:
        frame = tk.PhotoImage(file="/home/roza/nbfc/nyancat.gif", format="gif -index {}".format(len(frames)))
        frames.append(frame)
except Exception:
    pass

if frames:
    # Create a Label to display the nyancat animation
    nyan_label = tk.Label(root, bg="#2e2e2e")
    nyan_label.pack(pady=10)

    # Function to update the image frame
    def update_frame(ind):
        frame = frames[ind]
        nyan_label.configure(image=frame)
        ind = (ind + 1) % len(frames)
        root.after(100, update_frame, ind)  # update every 100ms

    # Start animation
    update_frame(0)
else:
    # Fallback in case the gif is missing or has no frames
    nyan_label = tk.Label(root, text="Nyan Cat not found", fg=label_fg, bg="#2e2e2e")
    nyan_label.pack(pady=10)

# Start the GUI event loop
root.mainloop()
