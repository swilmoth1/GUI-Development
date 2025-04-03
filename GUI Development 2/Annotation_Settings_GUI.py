import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math
import os
import json

class AnnotationSettingsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Annotation Settings")
        self.settings_file = "annotation_settings.json"
        self.recording_settings_file = "recording_settings.json"
        
        # Add material defaults
        self.material_defaults = MaterialDefaults()
        self.selected_material = tk.StringVar()
        self.use_material_defaults = tk.BooleanVar(value=False)
        
        # Initialize settings with defaults
        self.show_boxes = tk.BooleanVar(value=True)
        self.show_labels = tk.BooleanVar(value=True)
        
        # Initialize position checkboxes
        self.label_positions = {
            "top-left": tk.BooleanVar(value=True),
            "top-right": tk.BooleanVar(value=False),
            "bottom-left": tk.BooleanVar(value=False),
            "bottom-right": tk.BooleanVar(value=False)
        }
        
        # Initialize bottom left info fields (moved from bottom right)
        self.bottom_left_fields = {
            "Material": {"show": tk.BooleanVar(value=False), "value": tk.StringVar(value="")},
            "Job Number": {"show": tk.BooleanVar(value=False), "value": tk.StringVar(value="")},
            "Wire Feed Speed": {"show": tk.BooleanVar(value=False), "value": tk.StringVar(value="")},
            "Travel Speed": {"show": tk.BooleanVar(value=False), "value": tk.StringVar(value="")}
        }
        
        # Initialize bottom right camera info fields
        self.bottom_right_fields = {
            "Camera": {"show": tk.BooleanVar(value=False), "value": tk.StringVar(value="")},
            "Lens": {"show": tk.BooleanVar(value=False), "value": tk.StringVar(value="")},
            "Viewing Angle": {"show": tk.BooleanVar(value=False), "value": tk.StringVar(value="")},
            "Focus": {"show": tk.BooleanVar(value=False), "value": tk.StringVar(value="")},
            "Aperature": {"show": tk.BooleanVar(value=False), "value": tk.StringVar(value="")},
            "Distance": {"show": tk.BooleanVar(value=False), "value": tk.StringVar(value="")},
            "CTWD (mm)": {"show": tk.BooleanVar(value=False), "value": tk.StringVar(value="")}
        }
        
        # Initialize top right info fields - script-calculated and user-input fields
        self.top_right_fields = {
            # Script-calculated fields (no value entry needed)
            "FPS": {"show": tk.BooleanVar(value=False)},
            "Running": {"show": tk.BooleanVar(value=False)},
            "Output": {"show": tk.BooleanVar(value=False)},
            # User-input fields
            "Illum": {"show": tk.BooleanVar(value=False), "value": tk.StringVar(value="")},
            "Shielding Gas": {"show": tk.BooleanVar(value=False), "value": tk.StringVar(value="")},
            "Note": {"show": tk.BooleanVar(value=False), "value": tk.StringVar(value="")}
        }
        
        # Initialize top left fields - Time is script-calculated like FPS/Running/Output
        self.top_left_fields = {
            "Time": {"show": tk.BooleanVar(value=False)},  # Changed to match script-calculated style
            "FA": {"show": tk.BooleanVar(value=False), "value": tk.StringVar(value="")}
        }
        
        # Add ET field from recording settings
        self.et_field = {"show": tk.BooleanVar(value=False), "value": tk.StringVar(value="")}
        
        self.vars = {}  # Store all variables
        
        self.load_settings()
        self.create_widgets()

    