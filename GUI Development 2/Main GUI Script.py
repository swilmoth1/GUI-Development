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
import socket
import threading
from pypylon import pylon
import sys
import cv2

# Set theme and color
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Configuration
NUM_GRAPHS = 5  # Updated to 5 graphs
HISTORY_LENGTH = 100  # Number of frames to show in history
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
DEFAULT_IMG = os.path.join(ASSETS_DIR, "placeholder.png")

global frame_count
frame_count = 0
cam = 0
cam_lock = threading.Lock()

# Camera IP and port
IP = "169.254.235.230"
PORT = 139

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
    GraphSettingsGUI(window, callback = update_graphs)

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

is_recording = False

def toggle_recording():
    global is_recording
    if record_button.cget("text") == "Start Recording":
        record_button.configure(text="Stop Recording", 
                                fg_color="red",
                                hover_color="dark red")
        is_recording = True
        update_recording_loop()  # Start the loop
    else:
        record_button.configure(text="Start Recording", 
                                fg_color="green",
                                hover_color="dark green")
        is_recording = False     # Stop the loop

def update_recording_loop():
    if is_recording:
        raw_image, annotated_image = video_acquiring(recording_settings, annotation_settings)
        frame_dict = {
            "video_raw": raw_image,
            "video_annotated": annotated_image
        }
        draw_video_previews_from_frames(recording_settings, frame_dict)
        # Schedule this function to run again after 30 ms (approx ~30 fps)
        window.after(30, update_recording_loop)
    
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



def update_graphs():
    if os.path.exists("graph_settings.json"):
        with open("graph_settings.json", 'r') as f:
            global graph_settings 
            graph_settings = json.load(f)
            render_charts()

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
            global class_values 
            class_values = json.load(f)
            render_charts()
    
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
status_title = ctk.CTkLabel(status_frame, text="Recording Status:", font=("Arial", 12, "bold"))
status_title.grid(row=0,column=0,sticky="w", padx=10, pady=5)


camera_status_frame_title = ctk.CTkLabel(status_frame, text="Camera Status:", font=("Arial",12,"bold"))
camera_status_frame_title.grid(row=0,column=1,sticky="nsew",padx=10,pady=5)


# New big status display
big_status_display = ctk.CTkLabel(
    status_frame, 
    text="Idle",              # Example status text
    font=("Arial", 20, "bold"),       # Large font for emphasis
    text_color="yellow",               # Optional: use color to show status
    anchor="w"
)
big_status_display.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))


big_camera_display = ctk.CTkLabel(status_frame,
                                  text="Disconnected",
                                  font=("Arial", 20, "bold"),
                                  text_color="yellow",
                                  anchor="e")
big_camera_display.grid(row=1,column=1, sticky="ew", padx=10, pady= (5,10))
# Optional: make sure the frame expands with window resizing
status_frame.grid_columnconfigure(0, weight=1)

def set_ET_time(recording_settings,time):
    if recording_settings.get("et_mode") == "Fixed":
        return recording_settings.get("et_fixed"), 0  # Fixed mode, loop count always 0

    elif recording_settings.get("et_mode") == "Iterate":
        et_start = recording_settings.get("et_start")
        et_end = recording_settings.get("et_end")
        et_step = recording_settings.get("et_step")
        time_increment = recording_settings.get("et_time")

        # Total number of unique steps before looping
        total_steps = ((et_end - et_start) // et_step) + 1

        # How many time steps have passed
        steps_passed = int(time // time_increment)

        # Determine loop count and current step
        loop_count = steps_passed // total_steps
        current_step = steps_passed % total_steps

        # Calculate current exposure
        exposure_time = et_start + current_step * et_step

        return exposure_time, loop_count

def annotate_raw_image(frame, annotation_settings, exposure_time, loop_count, elapsed_time, fps):
    annotated_frame = frame
    frame_height, frame_width, _ = annotated_frame.shape

    ### ─── TOP LEFT ───────────────────────────────────────────────
    if annotation_settings["manual_settings"]["label_positions"].get("top-left"):
        line_offset = 0
        top_left_start_y = 30
        spacing = 20

        # Exposure Time
        cv2.putText(annotated_frame, f"ET: {exposure_time}", (10, top_left_start_y + spacing * line_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        line_offset += 1

        # Time
        if annotation_settings["manual_settings"]["top_left_fields"]["Time"].get("show"):
            text = annotation_settings["manual_settings"]["top_left_fields"]["Time"].get("value")
            cv2.putText(annotated_frame, f"Time: {text}", (10, top_left_start_y + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            line_offset += 1

        # FA
        if annotation_settings["manual_settings"]["top_left_fields"]["FA"].get("show"):
            text = annotation_settings["manual_settings"]["top_left_fields"]["FA"].get("value")
            cv2.putText(annotated_frame, f"FA: {text}", (10, top_left_start_y + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    ### ─── TOP RIGHT ──────────────────────────────────────────────
    if annotation_settings["manual_settings"]["label_positions"].get("top-right"):
        line_offset = 0
        top_right_start_y = 30
        spacing = 20

        fields = annotation_settings["manual_settings"]["top_right_fields"]
        for field in ["FPS", "Running", "Output", "Illum", "Shielding Gas", "Note"]:
            if fields[field].get("show"):
                text = f"{field}: {fields[field].get('value')}"
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                cv2.putText(annotated_frame, text,
                            (frame_width - text_size[0] - 10, top_right_start_y + spacing * line_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                line_offset += 1

    ### ─── BOTTOM LEFT ────────────────────────────────────────────
    if annotation_settings["manual_settings"]["label_positions"].get("bottom-left"):
        line_offset = 0
        bottom_left_start_y = frame_height - 100
        spacing = 20

        fields = annotation_settings["manual_settings"]["bottom_left_fields"]
        for field in ["Material", "Job Number", "Wire Feed Speed", "Travel Speed"]:
            if fields[field].get("show"):
                text = f"{field}: {fields[field].get('value')}"
                cv2.putText(annotated_frame, text,
                            (10, bottom_left_start_y + spacing * line_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                line_offset += 1

    ### ─── BOTTOM RIGHT ───────────────────────────────────────────
    if annotation_settings["manual_settings"]["label_positions"].get("bottom-right"):
        line_offset = 0
        bottom_right_start = frame_height - 120
        spacing = 20

        # Camera
        if annotation_settings["manual_settings"]["bottom_right_fields"]["Camera"].get("show"):
            text = annotation_settings["manual_settings"]["bottom_right_fields"]["Camera"].get("value")
            cv2.putText(annotated_frame, text,
                        (frame_width - 200, bottom_right_start + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            line_offset += 1

        # Lens + Viewing Angle
        fields = annotation_settings["manual_settings"]["bottom_right_fields"]
        show_lens = fields["Lens"].get("show")
        show_angle = fields["Viewing Angle"].get("show")
        lens_val = fields["Lens"].get("value")
        angle_val = fields["Viewing Angle"].get("value")

        if show_lens or show_angle:
            combined = []
            if show_lens:
                combined.append(lens_val)
            if show_angle:
                combined.append(angle_val)
            text = " | ".join(combined)
            cv2.putText(annotated_frame, text,
                        (frame_width - 200, bottom_right_start + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            line_offset += 1

        # Focus
        if fields["Focus"].get("show"):
            cv2.putText(annotated_frame, fields["Focus"].get("value"),
                        (frame_width - 200, bottom_right_start + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            line_offset += 1

        # Aperture (note: JSON typo was "Aperature" but use "Aperture" for consistency)
        if fields["Aperature"].get("show"):
            cv2.putText(annotated_frame, fields["Aperature"].get("value"),
                        (frame_width - 200, bottom_right_start + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            line_offset += 1

        # Distance
        if fields["Distance"].get("show"):
            text = f"Distance: {fields['Distance'].get('value')}"
            cv2.putText(annotated_frame, text,
                        (frame_width - 200, bottom_right_start + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            line_offset += 1

        # CTWD
        if fields["CTWD (mm)"].get("show"):
            text = f"dNtW (mm): {fields['CTWD (mm)'].get('value')}"
            cv2.putText(annotated_frame, text,
                        (frame_width - 200, bottom_right_start + spacing * line_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return annotated_frame

def calculate_fps(frame_count, start_time):
    # Calculate the fps of the video based on the current time, start time, and frames currently collected.
    elapsed_time = time.time() - start_time
    fps = frame_count / elapsed_time if elapsed_time > 0 else 0
    return fps, elapsed_time

def video_acquiring(recording_settings, annotation_settings):
    global frame_count
    start_time = time.time()
    elapsed_time = time.time() - start_time
    frame_count = frame_count + 1

    # Setup exposure time
    [exposure_time, loop_count] = set_ET_time(recording_settings, elapsed_time)
    camera.ExposureTimeRaw.SetValue(int(exposure_time))

    # Grab frame
    grab_result = camera.GrabOne(1000)

    raw_image = None
    annotated_image = None

    if grab_result and grab_result.IsValid() and grab_result.GrabSucceeded():
        img_array = grab_result.Array
        raw_rgb = cv2.cvtColor(img_array, cv2.COLOR_BAYER_BG2RGB)

        if recording_settings.get("video_raw"):
            raw_image = raw_rgb.copy()

        if recording_settings.get("video_annotated"):
            [fps, elapsed_time] = calculate_fps(frame_count, start_time)
            annotated_image = annotate_raw_image(
                raw_rgb.copy(),
                annotation_settings,
                exposure_time,
                loop_count,
                elapsed_time,
                fps,
            )
    else:
        print("❌ Grab failed or returned invalid result.")

    return raw_image, annotated_image

def establish_image_frames(recording_settings):
    preview_row = 1
    preview_col = 0
    i=1
    
    for key in ["video_raw", "video_annotated", "video_segmented"]:
        if recording_settings.get(key):
            image_frame.grid_columnconfigure(1, weight=1)


def draw_video_previews_from_frames(recording_settings, frame_dict):
    preview_row = 1
    preview_col = 0
    i = 1

    for key in ["video_raw", "video_annotated", "video_segmented"]:
        if recording_settings.get(key) and key in frame_dict:
            try:
                frame = frame_dict[key]
                
                # Convert BGR (OpenCV) to RGB (PIL)
                if frame is not None:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(frame_rgb)
                    img_pil = img_pil.resize((650, 450), Image.Resampling.LANCZOS)
                    photo_img = ImageTk.PhotoImage(img_pil)

                    image_frame.grid_columnconfigure(i, weight=1)

                    preview_frame = ctk.CTkFrame(master=image_frame)
                    preview_frame.grid(row=preview_row, column=preview_col, padx=10, pady=10)

                    # Display image
                    img_label = ctk.CTkLabel(master=preview_frame, image=photo_img, text="")
                    img_label.image = photo_img  # Prevent garbage collection
                    img_label.pack()

                    # Display label text
                    text = key.replace("_", " ").title()
                    text_label = ctk.CTkLabel(master=preview_frame, text=text)
                    text_label.pack(pady=(5, 0))

                    preview_col += 1
                    i += 1
            except Exception as e:
                print(f"Error displaying preview for {key}:", e)

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
                # photo_img = ctk.CTkImage(light_image=img, size=(550,400))  # auto-resizes

                # img_label = ctk.CTkLabel(master=preview_frame, image=photo_img, text="")
                # img_label.pack()

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
    ax.autoscale_view() 

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
            plot_feature_on_axes(ax,"Welding Wire",x_data = [0,1,2], y_data = [0,2,4],
                                 desired_value=int(data['Welding Wire']['x_average']['value']),
                                 tol_pos=int(data['Welding Wire']['x_average']['pos_tolerance']),
                                 tol_neg=int(data['Welding Wire']['x_average']['neg_tolerance']),
                                 title="X Average",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Arc Flash",x_data = [0,1,2], y_data = [0,3,6],
                                 desired_value=int(data['Arc Flash']['x_average']['value']),
                                 tol_pos=int(data['Arc Flash']['x_average']['pos_tolerance']),
                                 tol_neg=int(data['Arc Flash']['x_average']['neg_tolerance']),
                                 title="X Average",xlabel="Frame Index",ylabel="Pixel Value")
            canvas = FigureCanvasTkAgg(fig, master=x_average_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1,column=column_index)
            column_index=column_index+1
        if chart_metrics.get("X Maximum"):
            fig=Figure(figsize=(4,3),dpi=100)
            ax = fig.add_subplot(111)
            x_maximum_frame = ctk.CTkFrame(x_position_frame)
            x_maximum_frame.grid(row=1,column=column_index, sticky = "w", padx=10, pady=5)
            plot_feature_on_axes(ax,"Solidification Zone",x_data = [0,1,2], y_data = [0,1,2],
                                 desired_value=int(data['Solidification Zone']['x_max']['value']),
                                 tol_pos=int(data['Solidification Zone']['x_max']['pos_tolerance']),
                                 tol_neg=int(data['Solidification Zone']['x_max']['neg_tolerance']),
                                 title="X Maximum",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Welding Wire",x_data = [0,1,2], y_data = [0,2,4],
                                 desired_value=int(data['Welding Wire']['x_max']['value']),
                                 tol_pos=int(data['Welding Wire']['x_max']['pos_tolerance']),
                                 tol_neg=int(data['Welding Wire']['x_max']['neg_tolerance']),
                                 title="X Maximum",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Arc Flash",x_data = [0,1,2], y_data = [0,3,6],
                                 desired_value=int(data['Arc Flash']['x_max']['value']),
                                 tol_pos=int(data['Arc Flash']['x_max']['pos_tolerance']),
                                 tol_neg=int(data['Arc Flash']['x_max']['neg_tolerance']),
                                 title="X Maximum",xlabel="Frame Index",ylabel="Pixel Value")
            canvas = FigureCanvasTkAgg(fig, master=x_maximum_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1,column=column_index)
            column_index=column_index+1
            
        if chart_metrics.get("X Minimum"):
            fig=Figure(figsize=(4,3),dpi=100)
            ax = fig.add_subplot(111)
            x_minimum_frame = ctk.CTkFrame(x_position_frame)
            x_minimum_frame.grid(row=1,column=column_index, sticky = "w", padx=10, pady=5)
            plot_feature_on_axes(ax,"Solidification Zone",x_data = [0,1,2], y_data = [0,1,2],
                                 desired_value=int(data['Solidification Zone']['x_min']['value']),
                                 tol_pos=int(data['Solidification Zone']['x_min']['pos_tolerance']),
                                 tol_neg=int(data['Solidification Zone']['x_min']['neg_tolerance']),
                                 title="X Minimum",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Welding Wire",x_data = [0,1,2], y_data = [0,2,4],
                                 desired_value=int(data['Welding Wire']['x_min']['value']),
                                 tol_pos=int(data['Welding Wire']['x_min']['pos_tolerance']),
                                 tol_neg=int(data['Welding Wire']['x_min']['neg_tolerance']),
                                 title="X Minimum",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Arc Flash",x_data = [0,1,2], y_data = [0,3,6],
                                 desired_value=int(data['Arc Flash']['x_min']['value']),
                                 tol_pos=int(data['Arc Flash']['x_min']['pos_tolerance']),
                                 tol_neg=int(data['Arc Flash']['x_min']['neg_tolerance']),
                                 title="X Minimum",xlabel="Frame Index",ylabel="Pixel Value")
            canvas = FigureCanvasTkAgg(fig, master=x_minimum_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1,column=column_index)
            column_index=+1
            
            
    if show_charts.get("Y Position Values"):
        column_index=0
        y_position_frame = ctk.CTkFrame(chart_frame)
        y_position_frame_label = ctk.CTkLabel(y_position_frame, text= "Y Position Values", font=("Arial", 12, "bold"))
        y_position_frame.grid(row=1, column=0, padx=20, pady=20)
        y_position_frame_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        if chart_metrics.get("Y Average"):
            fig=Figure(figsize=(4,3),dpi=100)
            ax = fig.add_subplot(111)
            y_average_frame = ctk.CTkFrame(y_position_frame)
            y_average_frame.grid(row=1,column=column_index, sticky = "w", padx=10, pady=5)
            plot_feature_on_axes(ax,"Solidification Zone",x_data = [0,1,2], y_data = [0,1,2],
                                 desired_value=int(data['Solidification Zone']['y_average']['value']),
                                 tol_pos=int(data['Solidification Zone']['y_average']['pos_tolerance']),
                                 tol_neg=int(data['Solidification Zone']['y_average']['neg_tolerance']),
                                 title="Y Average",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Welding Wire",x_data = [0,1,2], y_data = [0,2,4],
                                 desired_value=int(data['Welding Wire']['y_average']['value']),
                                 tol_pos=int(data['Welding Wire']['y_average']['pos_tolerance']),
                                 tol_neg=int(data['Welding Wire']['y_average']['neg_tolerance']),
                                 title="Y Average",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Arc Flash",x_data = [0,1,2], y_data = [0,3,6],
                                 desired_value=int(data['Arc Flash']['y_average']['value']),
                                 tol_pos=int(data['Arc Flash']['y_average']['pos_tolerance']),
                                 tol_neg=int(data['Arc Flash']['y_average']['neg_tolerance']),
                                 title="Y Average",xlabel="Frame Index",ylabel="Pixel Value")
            canvas = FigureCanvasTkAgg(fig, master=y_average_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1,column=column_index)
            column_index=column_index+1
        if chart_metrics.get("Y Maximum"):
            fig=Figure(figsize=(4,3),dpi=100)
            ax = fig.add_subplot(111)
            y_maximum_frame = ctk.CTkFrame(y_position_frame)
            y_maximum_frame.grid(row=1,column=column_index, sticky = "w", padx=10, pady=5)
            plot_feature_on_axes(ax,"Solidification Zone",x_data = [0,1,2], y_data = [0,1,2],
                                 desired_value=int(data['Solidification Zone']['y_max']['value']),
                                 tol_pos=int(data['Solidification Zone']['y_max']['pos_tolerance']),
                                 tol_neg=int(data['Solidification Zone']['y_max']['neg_tolerance']),
                                 title="Y Maximum",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Welding Wire",x_data = [0,1,2], y_data = [0,2,4],
                                 desired_value=int(data['Welding Wire']['y_max']['value']),
                                 tol_pos=int(data['Welding Wire']['y_max']['pos_tolerance']),
                                 tol_neg=int(data['Welding Wire']['y_max']['neg_tolerance']),
                                 title="Y Maximum",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Arc Flash",x_data = [0,1,2], y_data = [0,3,6],
                                 desired_value=int(data['Arc Flash']['y_max']['value']),
                                 tol_pos=int(data['Arc Flash']['y_max']['pos_tolerance']),
                                 tol_neg=int(data['Arc Flash']['y_max']['neg_tolerance']),
                                 title="Y Maximum",xlabel="Frame Index",ylabel="Pixel Value")
            canvas = FigureCanvasTkAgg(fig, master=y_maximum_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1,column=column_index)
            column_index=column_index+1
            
        if chart_metrics.get("Y Minimum"):
            fig=Figure(figsize=(4,3),dpi=100)
            ax = fig.add_subplot(111)
            y_minimum_frame = ctk.CTkFrame(y_position_frame)
            y_minimum_frame.grid(row=1,column=column_index, sticky = "w", padx=10, pady=5)
            plot_feature_on_axes(ax,"Solidification Zone",x_data = [0,1,2], y_data = [0,1,2],
                                 desired_value=int(data['Solidification Zone']['y_min']['value']),
                                 tol_pos=int(data['Solidification Zone']['y_min']['pos_tolerance']),
                                 tol_neg=int(data['Solidification Zone']['y_min']['neg_tolerance']),
                                 title="Y Minimum",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Welding Wire",x_data = [0,1,2], y_data = [0,2,4],
                                 desired_value=int(data['Welding Wire']['y_min']['value']),
                                 tol_pos=int(data['Welding Wire']['y_min']['pos_tolerance']),
                                 tol_neg=int(data['Welding Wire']['y_min']['neg_tolerance']),
                                 title="Y Minimum",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Arc Flash",x_data = [0,1,2], y_data = [0,3,6],
                                 desired_value=int(data['Arc Flash']['y_min']['value']),
                                 tol_pos=int(data['Arc Flash']['y_min']['pos_tolerance']),
                                 tol_neg=int(data['Arc Flash']['y_min']['neg_tolerance']),
                                 title="Y Minimum",xlabel="Frame Index",ylabel="Pixel Value")
            canvas = FigureCanvasTkAgg(fig, master=y_minimum_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1,column=column_index)
            column_index=+1
    
    if show_charts.get("Position Standard Deviations"):
        column_index = 0
        position_std_frame = ctk.CTkFrame(chart_frame)
        position_std_frame_label = ctk.CTkLabel(position_std_frame, text= "Position Standard Deviation", font=("Arial", 12, "bold"))
        position_std_frame.grid(row=0, column=1, padx=20, pady=20)
        position_std_frame_label.grid(row=0,column=0,sticky="w", padx=10, pady=5)
        
        if chart_metrics.get("X Average Standard Deviation"):
            fig=Figure(figsize=(4,3),dpi=100)
            ax = fig.add_subplot(111)
            x_avg_std_dev_frame = ctk.CTkFrame(position_std_frame)
            x_avg_std_dev_frame.grid(row=1,column=column_index, sticky = "w", padx=10, pady=5)
            plot_feature_on_axes(ax,"Solidification Zone",x_data = [0,1,2], y_data = [0,1,2],
                                 desired_value=int(data['Solidification Zone']['x_avg_std_deviation']['value']),
                                 tol_pos=int(data['Solidification Zone']['x_avg_std_deviation']['pos_tolerance']),
                                 tol_neg=int(data['Solidification Zone']['x_avg_std_deviation']['neg_tolerance']),
                                 title="X Avg Std Dev",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Welding Wire",x_data = [0,1,2], y_data = [0,2,4],
                                 desired_value=int(data['Welding Wire']['x_avg_std_deviation']['value']),
                                 tol_pos=int(data['Welding Wire']['x_avg_std_deviation']['pos_tolerance']),
                                 tol_neg=int(data['Welding Wire']['x_avg_std_deviation']['neg_tolerance']),
                                 title="X Avg Std Dev",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Arc Flash",x_data = [0,1,2], y_data = [0,3,6],
                                 desired_value=int(data['Arc Flash']['x_avg_std_deviation']['value']),
                                 tol_pos=int(data['Arc Flash']['x_avg_std_deviation']['pos_tolerance']),
                                 tol_neg=int(data['Arc Flash']['x_avg_std_deviation']['neg_tolerance']),
                                 title="X Avg Std Dev",xlabel="Frame Index",ylabel="Pixel Value")
            canvas = FigureCanvasTkAgg(fig, master=x_avg_std_dev_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1,column=column_index)
            column_index=column_index+1
            
        if chart_metrics.get("Y Average Standard Deviation"):
            fig=Figure(figsize=(4,3),dpi=100)
            ax = fig.add_subplot(111)
            y_avg_std_dev_frame = ctk.CTkFrame(position_std_frame)
            y_avg_std_dev_frame.grid(row=1,column=column_index, sticky = "w", padx=10, pady=5)
            plot_feature_on_axes(ax,"Solidification Zone",x_data = [0,1,2], y_data = [0,1,2],
                                 desired_value=int(data['Solidification Zone']['y_avg_std_deviation']['value']),
                                 tol_pos=int(data['Solidification Zone']['y_avg_std_deviation']['pos_tolerance']),
                                 tol_neg=int(data['Solidification Zone']['y_avg_std_deviation']['neg_tolerance']),
                                 title="Y Avg Std Dev",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Welding Wire",x_data = [0,1,2], y_data = [0,2,4],
                                 desired_value=int(data['Welding Wire']['y_avg_std_deviation']['value']),
                                 tol_pos=int(data['Welding Wire']['y_avg_std_deviation']['pos_tolerance']),
                                 tol_neg=int(data['Welding Wire']['y_avg_std_deviation']['neg_tolerance']),
                                 title="Y Avg Std Dev",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Arc Flash",x_data = [0,1,2], y_data = [0,3,6],
                                 desired_value=int(data['Arc Flash']['y_avg_std_deviation']['value']),
                                 tol_pos=int(data['Arc Flash']['y_avg_std_deviation']['pos_tolerance']),
                                 tol_neg=int(data['Arc Flash']['y_avg_std_deviation']['neg_tolerance']),
                                 title="Y Avg Std Dev",xlabel="Frame Index",ylabel="Pixel Value")
            canvas = FigureCanvasTkAgg(fig, master=y_avg_std_dev_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1,column=column_index)
            column_index=column_index+1
      
        
    if show_charts.get("Class Area"):
        column_index = 0
        class_area_frame = ctk.CTkFrame(chart_frame)
        class_area_frame_label = ctk.CTkLabel(class_area_frame, text= "Class Area and Standard Deviation", font=("Arial", 12, "bold"))
        class_area_frame.grid(row=1, column=1, padx=20, pady=20)
        class_area_frame_label.grid(row=0,column=0,sticky="w", padx=10, pady=5)
        if chart_metrics.get("Class Area"):
            fig=Figure(figsize=(4,3),dpi=100)
            ax = fig.add_subplot(111)
            class_area_sub_frame = ctk.CTkFrame(class_area_frame)
            class_area_sub_frame.grid(row=1,column=column_index, sticky = "w", padx=10, pady=5)
            plot_feature_on_axes(ax,"Solidification Zone",x_data = [0,1,2], y_data = [0,1,2],
                                 desired_value=int(data['Solidification Zone']['area_average']['value']),
                                 tol_pos=int(data['Solidification Zone']['area_average']['pos_tolerance']),
                                 tol_neg=int(data['Solidification Zone']['area_average']['neg_tolerance']),
                                 title="Class Area",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Welding Wire",x_data = [0,1,2], y_data = [0,2,4],
                                 desired_value=int(data['Welding Wire']['area_average']['value']),
                                 tol_pos=int(data['Welding Wire']['area_average']['pos_tolerance']),
                                 tol_neg=int(data['Welding Wire']['area_average']['neg_tolerance']),
                                 title="Class Area",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Arc Flash",x_data = [0,1,2], y_data = [0,3,6],
                                 desired_value=int(data['Arc Flash']['area_average']['value']),
                                 tol_pos=int(data['Arc Flash']['area_average']['pos_tolerance']),
                                 tol_neg=int(data['Arc Flash']['area_average']['neg_tolerance']),
                                 title="Class Area",xlabel="Frame Index",ylabel="Pixel Value")
            canvas = FigureCanvasTkAgg(fig, master=class_area_sub_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1,column=column_index)
            column_index=column_index+1
            
    if show_charts.get("Class Area Standard Deviation"):
        if chart_metrics.get("Class Area"):
            fig=Figure(figsize=(4,3),dpi=100)
            ax = fig.add_subplot(111)
            class_std_dev_sub_frame = ctk.CTkFrame(class_area_frame)
            class_std_dev_sub_frame.grid(row=1,column=column_index, sticky = "w", padx=10, pady=5)
            plot_feature_on_axes(ax,"Solidification Zone",x_data = [0,1,2], y_data = [0,1,2],
                                 desired_value=int(data['Solidification Zone']['area_std_deviation']['value']),
                                 tol_pos=int(data['Solidification Zone']['area_std_deviation']['pos_tolerance']),
                                 tol_neg=int(data['Solidification Zone']['area_std_deviation']['neg_tolerance']),
                                 title="Standard Deviation",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Welding Wire",x_data = [0,1,2], y_data = [0,2,4],
                                 desired_value=int(data['Welding Wire']['area_std_deviation']['value']),
                                 tol_pos=int(data['Welding Wire']['area_std_deviation']['pos_tolerance']),
                                 tol_neg=int(data['Welding Wire']['area_std_deviation']['neg_tolerance']),
                                 title="Standard Deviation",xlabel="Frame Index",ylabel="Pixel Value")
            plot_feature_on_axes(ax,"Arc Flash",x_data = [0,1,2], y_data = [0,3,6],
                                 desired_value=int(data['Arc Flash']['area_std_deviation']['value']),
                                 tol_pos=int(data['Arc Flash']['area_std_deviation']['pos_tolerance']),
                                 tol_neg=int(data['Arc Flash']['area_std_deviation']['neg_tolerance']),
                                 title="Standard Deviation",xlabel="Frame Index",ylabel="Pixel Value")
            canvas = FigureCanvasTkAgg(fig, master=class_std_dev_sub_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1,column=column_index)
            column_index=column_index+1
        

   
    


# Graphical viewing
if any (graph_settings.get("show_charts",{}).values()):
    chart_window = ctk.CTkToplevel()
    chart_window.title("Charts Display")
    chart_window.geometry("800x600")
    # Chart container
    chart_frame = ctk.CTkFrame(chart_window)
    chart_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    
    render_charts()
    


def detect_basler_camera():
    try:
        tl_factory = pylon.TlFactory.GetInstance()
        devices = tl_factory.EnumerateDevices()
        return devices[0] if devices else None
    except Exception as e:
        print(f"Error detecting camera: {e}")
        return None

def update_status_loop(label):
    global cam, camera
    connected_once = False

    while not connected_once:
        # Show "Attempting to connect"
        label.after(0, lambda: label.configure(text="Attempting to connect", text_color="yellow"))

        device = detect_basler_camera()

        if device:
            try:
                cam_obj = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(device))
                cam_obj.Open()
                camera = cam_obj  # Store for later use
                connected_once = True

                # Update label to Connected
                label.after(0, lambda: label.configure(text="Connected", text_color="green"))

                with cam_lock:
                    cam = 1

                print(f"✅ Camera connected: {camera.GetDeviceInfo().GetModelName()}")
            except Exception as e:
                print(f"❌ Failed to open camera: {e}")
                label.after(0, lambda: label.configure(text="Disconnected", text_color="red"))
                with cam_lock:
                    cam = 0
        else:
            label.after(0, lambda: label.configure(text="Disconnected", text_color="red"))
            with cam_lock:
                cam = 0

        if not connected_once:
            time.sleep(2)
    

thread = threading.Thread(target=update_status_loop, args=(big_camera_display,), daemon=True)
thread.start()


#run
window.mainloop()
