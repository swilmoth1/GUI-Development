import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math
import os
import json
from Segmentation_Settings_GUI import SegmentationSettingsGUI
from Recording_settings_GUI import RecordingsettingsGUI
from Annotation_Settings_GUI import AnnotationSettingsGUI
from Material_Defaults_GUI import MaterialDefaultsGUI
from Graph_Settings_GUI import GraphSettingsGUI
from PIL import Image, ImageTk
from collections import deque
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Set theme and color
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Configuration
NUM_GRAPHS = 5  # Updated to 5 graphs
HISTORY_LENGTH = 100  # Number of frames to show in history
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
DEFAULT_IMG = os.path.join(ASSETS_DIR, "placeholder.png")

# Ensure assets directory exists
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

image_paths = {
    "video_raw": os.path.join(ASSETS_DIR, "Sample Raw Image.png"),
    "video_annotated": os.path.join(ASSETS_DIR, "Sample Annotated Image.png"),
    "video_segmented": os.path.join(ASSETS_DIR, "Sample Segmented Image.png"),
    "image_raw": os.path.join(ASSETS_DIR, "Sample Raw Image.png"),
    "image_annotated": os.path.join(ASSETS_DIR, "Sample Annotated Image.png"),
    "image_segmented": os.path.join(ASSETS_DIR, "Sample Segmented Image.png")
}

def load_image_preview(path, size=(160,120)):
    try:
        # Try to load specified image
        img = Image.open(path)
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        # Create a blank placeholder if image doesn't exist
        img = Image.new('RGB', size, color='gray')
        # Add text to indicate placeholder
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.text((10, size[1]//2), "No Preview", fill='white')
        # Save placeholder for future use
        img.save(path)
    
    try:
        img = img.resize(size, Image.Resampling.LANCZOS)
    except Exception as e:
        print(f"Error resizing image: {e}")
        img = img.resize(size, Image.NEAREST)
        
    return ctk.CTkImage(light_image=img, dark_image=img, size=size)

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
#control_frame.grid_columnconfigure(1, weight=1)  # Status section gets less space
control_title = ctk.CTkLabel(control_frame, text="Control Panel", font=("Arial", 12, "bold"))
control_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)

###### LOAD SETTINGS FROM BUTTON SELECTIONS

#read the json file for the Graph Settings
if os.path.exists("graph_settings.json"):
    with open("graph_settings.json", 'r') as f:
        graph_settings = json.load(f)

if os.path.exists("annotation_settings.json"):
    with open("annotation_settings.json", 'r') as f:
        annotation_settings = json.load(f)

if os.path.exists("class_values.json"):
    with open("class_values.json", 'r') as f:
        class_values = json.load(f)

if os.path.exists("material_defaults.json"):
    with open("material_defaults.json", 'r') as f:
        material_defaults = json.load(f)

if os.path.exists("recording_settings.json"):
    with open("recording_settings.json", 'r') as f:
        recording_settings = json.load(f)

# Buttons in Control Panel (stays in column 0)
buttons_frame = ctk.CTkFrame(control_frame)
buttons_frame.grid(row=1, column=0, padx=10, pady=5, sticky="w")

###############
def open_segmentation_settings():
    SegmentationSettingsGUI(window, callback = update_class_values)

def open_recording_settings():
    RecordingsettingsGUI(window, callback=update_gui_from_settings)
    
def open_annotation_settings():
    AnnotationSettingsGUI(window)
    
def open_material_defaults_settings():
    MaterialDefaultsGUI(window)

def open_graph_settings():
    GraphSettingsGUI(window)

def set_material_defaults(choice=None):
    if choice == "Select Material":
        return
    else:
        material_selection = choice

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

# Set default material selection
material_selection = list(material_defaults.keys())[0]

Material_selection_button = ctk.CTkComboBox(buttons_frame, values=["Select Material"]+list(material_defaults.keys()),command=set_material_defaults)
Material_selection_button.grid(row=0, column=5, padx=10, pady=5)
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
record_button.grid(row=0, column=6, padx=20, pady=10, sticky="ew")





def update_gui_from_settings():
    """Update GUI elements based on latest settings"""
    # Clear existing previews
    for widget in image_frame.winfo_children():
        widget.destroy()
    
    # Reload settings
    if os.path.exists("recording_settings.json"):
        with open("recording_settings.json", 'r') as f:
            recording_settings = json.load(f)
    
    # Add image viewing field to display image if the setting is selected
    draw_video_previews_from_json_selection(recording_settings)
    draw_image_previews_from_json_selection(recording_settings)

def update_class_values():
    if os.path.exists("class_values.json"):
        with open("class_values.json", 'r') as f:
            class_values = json.load(f)
    
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

status_frame = ctk.CTkFrame(master=window)
status_frame.grid(row=2,column=0,sticky="nsew", padx=10, pady=10)
status_title = ctk.CTkLabel(status_frame, text="Status", font=("Arial", 12, "bold"))
status_title.grid(row=0,column=0,sticky="w", padx=10, pady=5)


# New big status display
big_status_display = ctk.CTkLabel(
    status_frame, 
    text="Idle",              # Example status text
    font=("Arial", 20, "bold"),       # Large font for emphasis
    text_color="yellow",               # Optional: use color to show status
    anchor="w"
)
big_status_display.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))

# Optional: make sure the frame expands with window resizing
status_frame.grid_columnconfigure(0, weight=1)


def draw_video_previews_from_json_selection(recording_settings):
    # Add image viewing field to display image if the setting is selected in the submenu.
    preview_row = 1
    preview_col = 0
    i=1
    
    for key in ["video_raw", "video_annotated", "video_segmented"]:
        if recording_settings.get(key):
            try:
                image_frame.grid_columnconfigure(i, weight=1)
                # Load and resize image with proper parameters
                img = Image.open(image_paths[key])
                # img = img.resize((650, 450), Image.Resampling.LANCZOS)  # Fixed resize parameters
                photo_img = ImageTk.PhotoImage(img)

                # Create a sub-frame to hold image + label
                preview_frame = ctk.CTkFrame(master=image_frame)
                preview_frame.grid(row=preview_row, column=preview_col, padx=10, pady=10)

                # Image label (no text)
                photo_img = ctk.CTkImage(light_image=img, size=(550,400))  # auto-resizes

                img_label = ctk.CTkLabel(master=preview_frame, image=photo_img, text="")
                img_label.pack()

                # Text label underneath
                text = key.replace("_", " ").title()
                text_label = ctk.CTkLabel(master=preview_frame, text=text)
                text_label.pack(pady=(5, 0))

                preview_col += 1
                i += 1 
            except Exception as e:
                print(f"Error loading {key} preview:", e)
                
def draw_image_previews_from_json_selection(recording_settings):
    # Add image viewing field to display image if the setting is selected in the submenu.
    preview_row = 1
    preview_col = 0
    i=1
    
    for key in ["image_raw", "image_annotated", "image_segmented"]:
        if recording_settings.get(key):
            try:
                image_frame.grid_columnconfigure(i, weight=1)
                # Load and resize image with proper parameters
                img = Image.open(image_paths[key])
                # img = img.resize((650, 450), Image.Resampling.LANCZOS)  # Fixed resize parameters
                photo_img = ImageTk.PhotoImage(img)

                # Create a sub-frame to hold image + label
                preview_frame = ctk.CTkFrame(master=image_frame)
                preview_frame.grid(row=preview_row, column=preview_col, padx=10, pady=10)

                # Image label (no text)
                photo_img = ctk.CTkImage(light_image=img, size=(550,400))  # auto-resizes

                img_label = ctk.CTkLabel(master=preview_frame, image=photo_img, text="")
                img_label.pack()

                # Text label underneath
                text = key.replace("_", " ").title()
                text_label = ctk.CTkLabel(master=preview_frame, text=text)
                text_label.pack(pady=(5, 0))

                preview_col += 1
                i += 1 
            except Exception as e:
                print(f"Error loading {key} preview:", e)
                
draw_video_previews_from_json_selection(recording_settings)
draw_image_previews_from_json_selection(recording_settings)


def plot_feature_on_axes(ax, feature_name, x_data, y_data, desired_value, tol_pos, tol_neg, title, xlabel, ylabel):
    
    FEATURE_COLORS = {
    "Solidification Zone": "#1f77b4",
    "Welding Wire": "#ff7f0e",
    "Arc Flash": "#2ca02c"
    }
    
    color = FEATURE_COLORS.get(feature_name, "black")

    ax.plot(x_data, y_data, label=feature_name, color=color)
    ax.axhline(desired_value, color=color, linestyle='--', linewidth=1)
    ax.fill_between(x_data, desired_value - tol_neg, desired_value + tol_pos, color=color, alpha=0.2)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()

def render_charts():
    # Clear the frame first
    for widget in chart_frame.winfo_children():
        widget.destroy()
   

    # Draw frames for each graph type
    
    show_charts = graph_settings.get("show_charts", {})
    chart_metrics = graph_settings.get("metrics",{})
    
    # Define tolerance and good values
    material_selection 
    data=class_values[material_selection]
    
    if show_charts.get("X Position Values"):
        column_index=0
        x_position_frame = ctk.CTkFrame(chart_frame)
        x_position_frame_label = ctk.CTkLabel(x_position_frame, text= "X Position Values", font=("Arial", 12, "bold"))
        x_position_frame.grid(row=0, column=column_index, padx=20, pady=20)
        x_position_frame_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        if chart_metrics.get("X Average"):
            fig=Figure(figsize=(4,3),dpi=100)
            ax = fig.add_subplot(111)
            x_average_frame = ctk.CTkFrame(x_position_frame)
            x_average_frame.grid(row=1,column=column_index, sticky = "w", padx=10, pady=5)
            plot_feature_on_axes(ax,"Solidification Zone",x_data = [0,1,2], y_data = [0,1,2],
                                 desired_value=int(data['Solidification Zone']['x_average']['value']),
                                 tol_pos=int(data['Solidification Zone']['x_average']['pos_tolerance']),
                                 tol_neg=int(data['Solidification Zone']['x_average']['neg_tolerance']),
                                 title="X Average",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Welding Wire",x_data = [0,1,2], y_data = [0,2,4],desired_value=0,
                                 tol_pos=1,tol_neg=-2,title="X Average",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Arc Flash",x_data = [0,1,2], y_data = [0,3,6],desired_value=0,
                                 tol_pos=1,tol_neg=-2,title="X Average",xlabel="Frame Index",ylabel="Pixel Value")
            canvas = FigureCanvasTkAgg(fig, master=x_average_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1,column=column_index)
            column_index=+1
        if chart_metrics.get("X Maximum"):
            fig=Figure(figsize=(4,3),dpi=100)
            ax = fig.add_subplot(111)
            x_maximum_frame = ctk.CTkFrame(x_position_frame)
            x_maximum_frame.grid(row=1,column=column_index, sticky = "w", padx=10, pady=5)
            plot_feature_on_axes(ax,"Solidification Zone",x_data = [0,1,2], y_data = [0,1,2],desired_value=0,
                                 tol_pos=1,tol_neg=-2,title="X Maximum",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Welding Wire",x_data = [0,1,2], y_data = [0,2,4],desired_value=0,
                                 tol_pos=1,tol_neg=-2,title="X Maximum",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Arc Flash",x_data = [0,1,2], y_data = [0,2,4],desired_value=0,
                                 tol_pos=1,tol_neg=-2,title="X Maximum",xlabel="Frame Index",ylabel="Pixel Value")
            canvas = FigureCanvasTkAgg(fig, master=x_maximum_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1,column=column_index)
            column_index=+1
            
        if chart_metrics.get("X Minimum"):
            fig=Figure(figsize=(4,3),dpi=100)
            ax = fig.add_subplot(111)
            x_minimum_frame = ctk.CTkFrame(x_position_frame)
            x_minimum_frame.grid(row=1,column=column_index, sticky = "w", padx=10, pady=5)
            plot_feature_on_axes(ax,"Solidification Zone",x_data = [0,1,2], y_data = [0,1,2],desired_value=0,
                                 tol_pos=1,tol_neg=-2,title="X Maximum",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Welding Wire",x_data = [0,1,2], y_data = [0,2,4],desired_value=0,
                                 tol_pos=1,tol_neg=-2,title="X Maximum",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Arc Flash",x_data = [0,1,2], y_data = [0,2,4],desired_value=0,
                                 tol_pos=1,tol_neg=-2,title="X Maximum",xlabel="Frame Index",ylabel="Pixel Value")
            canvas = FigureCanvasTkAgg(fig, master=x_minimum_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1,column=column_index)
            column_index=+1
            
            
    if show_charts.get("Y Position Values"):
        y_position_frame = ctk.CTkFrame(chart_frame)
        y_position_frame_label = ctk.CTkLabel(y_position_frame, text= "Y Position Values", font=("Arial", 12, "bold"))
        y_position_frame.grid(row=1, column=0, padx=20, pady=20)
        y_position_frame_label.grid(row=0,column=0,sticky="w", padx=10, pady=5)
    
    if show_charts.get("Position Standard Deviations"):
        position_std_frame = ctk.CTkFrame(chart_frame)
        position_std_frame_label = ctk.CTkLabel(position_std_frame, text= "Position Standard Deviation", font=("Arial", 12, "bold"))
        position_std_frame.grid(row=2, column=0, padx=20, pady=20)
        position_std_frame_label.grid(row=0,column=0,sticky="w", padx=10, pady=5)
        
    if show_charts.get("Class Area"):
        class_area_frame = ctk.CTkFrame(chart_frame)
        class_area_frame_label = ctk.CTkLabel(class_area_frame, text= "Class Area", font=("Arial", 12, "bold"))
        class_area_frame.grid(row=3, column=0, padx=20, pady=20)
        class_area_frame_label.grid(row=0,column=0,sticky="w", padx=10, pady=5)
        
    if show_charts.get("Class Area Standard Deviation"):
        class_area_std_frame = ctk.CTkFrame(chart_frame)
        class_area_std_frame_label = ctk.CTkLabel(class_area_std_frame, text= "Class Area Standard Deviation", font=("Arial", 12, "bold"))
        class_area_std_frame.grid(row=4, column=0, padx=20, pady=20)
        class_area_std_frame_label.grid(row=0,column=0,sticky="w", padx=10, pady=5)
        
                
    row = 0

    def add_chart(title, x_data, y_data):
        nonlocal row
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(x_data, y_data)
        ax.set_title(title)
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=row, column=0, padx=10, pady=10)
        row += 1

    # Dummy data for now — replace with your real data
    sample_x = list(range(10))
    sample_y = [x**0.5 for x in sample_x]

    # Check and draw each chart conditionally
    

    if show_charts.get("X Position Values"):
        add_chart("X Position Values", sample_x, sample_y)

    if show_charts.get("Y Position Values"):
        add_chart("Y Position Values", sample_x, [x * 0.8 for x in sample_y])

    if show_charts.get("Position Standard Deviations"):
        add_chart("Position Std Devs", sample_x, [0.1 * (x % 3) for x in sample_x])

    if show_charts.get("Class Area"):
        add_chart("Class Area", sample_x, [x * 3 for x in sample_x])

    if show_charts.get("Class Area Standard Deviation"):
        add_chart("Class Area Std Dev", sample_x, [x * 0.5 for x in sample_x])

# Graphical viewing
if any (graph_settings.get("show_charts",{}).values()):
    chart_window = ctk.CTkToplevel()
    chart_window.title("Charts Display")
    chart_window.geometry("800x600")
    # Chart container
    chart_frame = ctk.CTkFrame(chart_window)
    chart_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    
    render_charts()
    
    

# # Add Graphical Viewing Field with fixed minimum size
# graph_frame = ctk.CTkFrame(master=window)
# graph_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
# graph_frame.grid_columnconfigure(0, weight=1)
# graph_frame.grid_rowconfigure(0, weight=0)  # Title row doesn't expand
# graph_frame.grid_rowconfigure(1, weight=1)  # Content row expands
# graph_frame.grid_propagate(False)  # Prevent frame from shrinking
# graph_frame.configure(height=400)  # Set minimum height

# graph_title = ctk.CTkLabel(graph_frame, text="Graphs", font=("Arial", 12, "bold"))
# graph_title.grid(row=0, column=0, sticky="w", padx=10, pady=5)

# # Load settings from graphical json
# show_charts = graph_settings.get("show_charts", {})
# chart_groups = graph_settings.get("chart_groups", {})
# metrics = graph_settings.get("metrics",{})

# chart_container = ctk.CTkFrame(graph_frame)
# chart_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
# chart_container.grid_columnconfigure((0, 1, 2), weight=1)
# chart_container.grid_rowconfigure((0, 1), weight=1)

# # Dummy data — replace with real values
# dummy_data = {
#     "X Average": [1, 2, 3],
#     "X Maximum": [2, 3, 4],
#     "X Minimum": [0, 1, 2],
#     "Y Average": [4, 5, 6],
#     "Y Maximum": [6, 7, 8],
#     "Y Minimum": [2, 3, 4],
#     "X Average Standard Deviation": [0.1, 0.2, 0.15],
#     "Y Average Standard Deviation": [0.2, 0.3, 0.25],
#     "Class Area": [10, 15, 20],
#     "Class Area Standard Deviation": [1, 1.5, 2]
# }


# # Set thresholds with separate positive and negative tolerances
# thresholds = {
#     "X Average": 2,  # Example threshold for X Average
#     "Y Average": 5,  # Example threshold for Y Average
# }

# # Set positive and negative tolerances for each metric
# positive_tolerances = {
#     "X Average": 0.5,  # Positive tolerance for X Average
#     "Y Average": 0.3,  # Positive tolerance for Y Average
# }

# negative_tolerances = {
#     "X Average": 0.2,  # Negative tolerance for X Average
#     "Y Average": 0.4,  # Negative tolerance for Y Average
# }


# # Set the initial row and column positions for the grid layout
# row = 1
# col = 0

# # Create subplots based on visible charts
# visible_charts = [(name, chart_groups[name]) for name, show in show_charts.items() if show and name in chart_groups]
# n = len(visible_charts)

# if n == 0:
#     # If no charts are selected, show a message
#     no_graph_label = ctk.CTkLabel(graph_frame, text="No charts selected.")
#     no_graph_label.grid(row=1, column=0)
# else:
#     # 3 columns, 2 rows grid layout
#     cols = 3
#     rows = 2

#     fig, axs = plt.subplots(rows, cols, figsize=(cols * 5, rows * 3.5))
#     axs = axs.flatten()  # Flatten in case we have a 2D array of axes

#     # Loop through and create the graphs
#     for i, (title, metric_keys) in enumerate(visible_charts):
#         ax = axs[i]
        
#         for metric in metric_keys:
#             if metrics.get(metric, False):
#                 ax.plot(dummy_data.get(metric, []), label=metric)
                
#                 # If a threshold is defined for the metric, add shaded areas for positive and negative tolerance
#                 if metric in thresholds:
#                     threshold = thresholds[metric]
#                     pos_tol = positive_tolerances.get(metric, 0)
#                     neg_tol = negative_tolerances.get(metric, 0)

#                     # Plot shaded area for positive tolerance (green)
#                     ax.fill_between(range(len(dummy_data.get(metric, []))),
#                                     threshold, threshold + pos_tol,
#                                     color='green', alpha=0.3, label=f"{metric} + tolerance")
                    
#                     # Plot shaded area for negative tolerance (red)
#                     ax.fill_between(range(len(dummy_data.get(metric, []))),
#                                     threshold, threshold - neg_tol,
#                                     color='red', alpha=0.3, label=f"{metric} - tolerance")

#         ax.set_title(title)
#         ax.legend(fontsize="small")
#         ax.grid(True)

#     # Hide unused subplots if there are fewer than 6 charts
#     for ax in axs[n:]:
#         ax.axis("off")

#     fig.tight_layout()

#     # Embed the figure in the existing graph_frame
#     canvas = FigureCanvasTkAgg(fig, master=graph_frame)
#     canvas_widget = canvas.get_tk_widget()
#     canvas_widget.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
            
            








#run
window.mainloop()
