import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math
from Segmentation_Settings_GUI import SegmentationSettingsGUI
from Recording_settings_GUI import RecordingsettingsGUI
from Annotation_Settings_GUI import AnnotationSettingsGUI
from Material_Defaults_GUI import MaterialDefaultsGUI
from Graph_Settings_GUI import GraphSettingsGUI
# Set theme and color
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Configuration
NUM_GRAPHS = 4  # Change this number to adjust the number of graphs

def on_closing():
    """Handle cleanup when main window is closed"""
    # Close all matplotlib figures
    plt.close('all')
    
    # Destroy any child windows
    for widget in window.winfo_children():
        if isinstance(widget, ctk.CTkToplevel):
            widget.destroy()
    
    # Cancel any pending after callbacks
    window.after_cancel(window.after_id)
    
    # Quit and destroy main window
    window.quit()
    window.destroy()

# Main GUI Window   
window = ctk.CTk()
window.title("Deposition Monitoring System")
window.protocol("WM_DELETE_WINDOW", on_closing)

# Store the first after callback ID
window.after_id = window.after(10, lambda: None)

#Testing messages
alert_message = tk.StringVar()
alert_message.set('Test')

# Maximize window while keeping controls
window.state('zoomed')  # For Windows

# Configure the main window's grid
window.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(1, weight=3)  # Image frame gets 3 parts
window.grid_rowconfigure(2, weight=3)  # Graph frame gets 3 parts
window.grid_rowconfigure(0, weight=1)  # Control panel gets 1 part

# Control panel field
control_frame = ctk.CTkFrame(master=window)
control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
control_frame.grid_columnconfigure(0, weight=4)  # Main buttons section gets more space
control_frame.grid_columnconfigure(1, weight=1)  # Status section gets less space
control_title = ctk.CTkLabel(control_frame, text="Control Panel", font=("Arial", 12, "bold"))
control_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)

# Update status frame position with larger size
status_frame = ctk.CTkFrame(control_frame)
status_frame.grid(row=1, column=1, padx=20, pady=10, sticky="ne")

status_label = ctk.CTkLabel(status_frame, 
                           text="Status:", 
                           font=("Arial", 14, "bold"))
status_label.grid(row=0, column=0, padx=15, pady=10)

status_value = ctk.CTkLabel(status_frame, 
                           text="Idle", 
                           font=("Arial", 16, "bold"),
                           text_color="yellow")
status_value.grid(row=0, column=1, padx=15, pady=10)

# Buttons in Control Panel (stays in column 0)
buttons_frame = ctk.CTkFrame(control_frame)
buttons_frame.grid(row=1, column=0, padx=10, pady=5, sticky="w")

###############
def open_segmentation_settings():
    SegmentationSettingsGUI(window)

def open_recording_settings():
    RecordingsettingsGUI(window)
    
def open_annotation_settings():
    AnnotationSettingsGUI(window)
    
def open_material_defaults_settings():
    MaterialDefaultsGUI(window)

def open_graph_settings():
    GraphSettingsGUI(window)
    
seg_settings_button = ctk.CTkButton(buttons_frame, 
                                  text="Segmentation Settings",
                                  command=open_segmentation_settings)
seg_settings_button.grid(row=0, column=0, padx=10, pady=5)

recording_settings_button = ctk.CTkButton(buttons_frame, text="Recording Settings", command=open_recording_settings)
recording_settings_button.grid(row=0, column=1, padx=10, pady=5)

Annotation_settings_button = ctk.CTkButton(buttons_frame, 
                                         text="Annotation Settings",
                                         command=open_annotation_settings)
Annotation_settings_button.grid(row=0, column=2, padx=10, pady=5)

Graph_settings_button = ctk.CTkButton(buttons_frame, text="Graph Settings", command=open_graph_settings)
Graph_settings_button.grid(row=0, column=3, padx=10, pady=5)

Material_defaults_button = ctk.CTkButton(buttons_frame, text="Material Defaults", command=open_material_defaults_settings)
Material_defaults_button.grid(row=0, column=4, padx=10, pady=5)
###############

def toggle_recording():
    current_text = record_button.cget("text")
    if current_text == "Start Recording":
        record_button.configure(text="Stop Recording", 
                              fg_color="red",
                              hover_color="dark red")
    else:
        record_button.configure(text="Start Recording", 
                              fg_color="green",
                              hover_color="dark green")

# Replace the record button section with:
record_button = ctk.CTkButton(buttons_frame, 
                             text="Start Recording",
                             command=toggle_recording,
                             font=("Arial", 16, "bold"),
                             fg_color="green",
                             hover_color="dark green",
                             width=200,
                             height=50)
record_button.grid(row=0, column=5, padx=20, pady=10, sticky="ew")

# Add Image Viewing Field with fixed minimum size
image_frame = ctk.CTkFrame(master=window)
image_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
image_frame.grid_columnconfigure(0, weight=1)
image_frame.grid_rowconfigure(0, weight=0)  # Title row doesn't expand
image_frame.grid_rowconfigure(1, weight=1)  # Content row expands
image_frame.grid_propagate(False)  # Prevent frame from shrinking
image_frame.configure(height=400)  # Set minimum height

image_title = ctk.CTkLabel(image_frame, text="Images", font=("Arial", 12, "bold"))
image_title.grid(row=0, column=0, sticky="w", padx=10, pady=5)

# Add Graphical Viewing Field with fixed minimum size
graph_frame = ctk.CTkFrame(master=window)
graph_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
graph_frame.grid_columnconfigure(0, weight=1)
graph_frame.grid_rowconfigure(0, weight=0)  # Title row doesn't expand
graph_frame.grid_rowconfigure(1, weight=1)  # Content row expands
graph_frame.grid_propagate(False)  # Prevent frame from shrinking
graph_frame.configure(height=400)  # Set minimum height

graph_title = ctk.CTkLabel(graph_frame, text="Graphs", font=("Arial", 12, "bold"))
graph_title.grid(row=0, column=0, sticky="w", padx=10, pady=5)

# Calculate grid layout for graphs
num_cols = min(3, NUM_GRAPHS)  # Maximum 3 graphs per row
num_rows = math.ceil(NUM_GRAPHS / num_cols)

# Create a figure with fixed size
fig, axes = plt.subplots(num_rows, num_cols, figsize=(12, 6))  # Fixed figure size
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

# Flatten axes array if multiple rows/columns
if NUM_GRAPHS > 1:
    axes = axes.flatten()

# Remove extra subplots if any
if NUM_GRAPHS > 1:
    for i in range(NUM_GRAPHS, len(axes)):
        fig.delaxes(axes[i])

fig.tight_layout()
canvas.draw()

#run
window.mainloop()
