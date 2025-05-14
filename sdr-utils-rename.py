#!/usr/bin/env python3

import sys
import re

# Append the DaVinci Resolve scripting modules path (macOS default)
dvrscript_module_path = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
if dvrscript_module_path not in sys.path:
    sys.path.append(dvrscript_module_path)

import DaVinciResolveScript as dvr_script  # type: ignore
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

resolve = dvr_script.scriptapp("Resolve")
if not resolve:
    raise RuntimeError("Failed to connect to Resolve")

project_manager = resolve.GetProjectManager()
project = project_manager.GetCurrentProject()
if not project:
    raise RuntimeError("No project is currently open.")

# Get all timelines
timeline_count = project.GetTimelineCount()
timelines = [project.GetTimelineByIndex(i + 1) for i in range(timeline_count)]
timeline_data = [(tl.GetName(), tl) for tl in timelines]

# GUI
root = tk.Tk()
root.title("Svjato's DaVinci Resolve Utils")
root.geometry("560x1000")  # Set window size

# Styling
root.configure(bg="#28282E")  # Dark background color
font_large = ("San Francisco", 20, "bold")
font_normal = ("San Francisco", 12)

# Title Label
title_label = tk.Label(root, text="SDRUtil | Timeline Rename v2", font=("San Francisco", 20, "bold"), fg="white", bg="#28282E")
title_label.pack(pady=20)

# Scrollable frame for timeline checkboxes
frame = tk.Frame(root, bg="#28282E")
frame.pack(pady=5, fill="both", expand=True)

# Add a Canvas for scrolling
canvas = tk.Canvas(frame, bg="#28282E", bd=0)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

timeline_frame = tk.Frame(canvas, bg="#28282E")
canvas_window = canvas.create_window((0, 0), window=timeline_frame, anchor="nw")

def resize_timeline_frame(event):
    canvas.itemconfig(canvas_window, width=event.width)

canvas.bind("<Configure>", resize_timeline_frame)

def update_previews(*args):
    find = find_var.get()
    replace = replace_var.get()
    for i, (name, _) in enumerate(timeline_data):
        if find:
            new_name = name.replace(find, replace)
            preview_text = f"{name} ➞ {new_name}" if new_name != name else name
        else:
            preview_text = name  # No "find" string, show original only
        checkbuttons[i].config(text=preview_text)

vars = []
checkbuttons = []

for name, _ in timeline_data:
    var = tk.BooleanVar()
    cb = tk.Checkbutton(
        timeline_frame,
        text=name,
        variable=var,
        anchor="w",
        width=50,
        bg="#28282E",
        fg="white",
        font=font_normal,
        selectcolor="#4E5A65"
    )
    cb.pack(fill="x", padx=10, pady=2)
    vars.append(var)
    checkbuttons.append(cb)

# Find/Replace input section
tk.Label(root, text="Find:", font=font_normal, fg="white", bg="#28282E").pack(pady=(10, 5))
find_var = tk.StringVar()
find_entry = tk.Entry(root, textvariable=find_var, font=font_normal, width=40)
find_entry.pack(pady=5)

tk.Label(root, text="Replace:", font=font_normal, fg="white", bg="#28282E").pack(pady=5)
replace_var = tk.StringVar()
replace_entry = tk.Entry(root, textvariable=replace_var, font=font_normal, width=40)
replace_entry.pack(pady=5)

find_var.trace_add("write", update_previews)
replace_var.trace_add("write", update_previews)

# Rename logic
def rename_timelines():
    find = find_var.get()
    replace = replace_var.get()
    if not find:
        messagebox.showerror("Error", "Find string cannot be empty.")
        return

    count = 0
    for i, (name, tl) in enumerate(timeline_data):
        if vars[i].get():
            new_name = name.replace(find, replace)
            if new_name != name:
                tl.SetName(new_name)
                count += 1

    messagebox.showinfo("Done", f"Renamed {count} timeline(s).")

# Apply Rename button with improved style
rename_button = tk.Button(root, text="Apply Rename", command=rename_timelines, font=font_large, bg="#28282E", fg="#28282E", relief="flat", height=2, width=15)
rename_button.pack(pady=20)

# Run the application
root.mainloop()
