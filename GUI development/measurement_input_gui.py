import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import os
import sys
from material_defaults import MaterialDefaults  # Add this import at the top
from gui.annotation_settings_gui import AnnotationSettingsGUI
from gui.recording_settings_gui import RecordingSettingsGUI
from gui.segmentation_settings_gui import SegmentationAndClassGUI
from gui.graph_settings_gui import GraphSettingsGUI
from gui.material_defaults_gui import MaterialDefaultsGUI
from gui.image_display import ImageDisplayFrame


class SegmentationAndClassGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Segmentation Settings")
        
        # Class Value settings
        self.classes = ["Welding Wire", "Solidification Zone", "Arc Flash"]
        self.fields = [
            "x_min", "x_max", "y_min", "y_max", "y_average", "x_average", 
            "area_average", "area_std_deviation", "y_avg_std_deviation", "x_avg_std_deviation"
        ]
        self.data_file = "class_values.json"
        self.settings_file = "segmentation_settings.json"
        
        # Segmentation settings
        self.apply_segmentation = tk.BooleanVar(value=False)
        self.compare_values = tk.BooleanVar(value=False)
        
        self.default_values = self.load_values()
        self.comparative_values = self.load_values()  # Add this line
        # Create validator for numeric input
        self.validate_numeric = self.root.register(self.validate_entry)
        self.entries = {}
        self.load_segmentation_settings()
        
        # Create main notebook for all tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Create tabs
        self.create_segmentation_tab()
        self.class_values_tab = None  # Initialize as None
        
        # Bind the segmentation settings change to update tabs
        self.apply_segmentation.trace('w', self.update_tabs)
        self.compare_values.trace('w', self.update_tabs)

    def create_segmentation_tab(self):
        seg_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(seg_frame, text="Segmentation Settings")
        
        # Segmentation checkboxes
        ttk.Checkbutton(seg_frame, text="Apply segmentation model",
                       variable=self.apply_segmentation,
                       command=self.handle_segmentation_toggle).pack(anchor="w", pady=5)
        
        self.compare_checkbox = ttk.Checkbutton(seg_frame, text="Compare values to Class Value Settings",
                                              variable=self.compare_values)
        self.compare_checkbox.pack(anchor="w", padx=20, pady=5)
        
        if not self.apply_segmentation.get():
            self.compare_checkbox.configure(state='disabled')

    def create_class_values_tab(self):
        if self.class_values_tab:
            self.notebook.forget(self.class_values_tab)
        
        self.class_values_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.class_values_tab, text="Class Values")
        
        # Create class notebook within the tab
        class_notebook = ttk.Notebook(self.class_values_tab)
        class_notebook.pack(expand=True, fill="both", pady=10)
        
        for class_name in self.classes:
            frame = ttk.Frame(class_notebook)
            class_notebook.add(frame, text=class_name)
            
            # Add header labels
            tk.Label(frame, text="Field").grid(row=0, column=0, padx=5, pady=2, sticky='w')
            tk.Label(frame, text="Value").grid(row=0, column=1, padx=5, pady=2, sticky='w')
            tk.Label(frame, text="+Tolerance").grid(row=0, column=2, padx=5, pady=2, sticky='w')
            tk.Label(frame, text="-Tolerance").grid(row=0, column=3, padx=5, pady=2, sticky='w')
            
            self.entries[class_name] = {}
            for row, field in enumerate(self.fields, start=1):
                # Field label
                tk.Label(frame, text=field).grid(row=row, column=0, padx=5, pady=2, sticky='w')
                
                # Value entry
                value_entry = ttk.Entry(frame, width=10, validate="key",
                                      validatecommand=(self.validate_numeric, '%P'))
                value_entry.grid(row=row, column=1, padx=5, pady=2)
                value_entry.insert(0, self.comparative_values[class_name][field])
                self.entries[class_name][field] = value_entry
                
                # Positive tolerance entry
                pos_tolerance_entry = ttk.Entry(frame, width=8, validate="key",
                                          validatecommand=(self.validate_numeric, '%P'))
                pos_tolerance_entry.grid(row=row, column=2, padx=5, pady=2)
                pos_tolerance_entry.insert(0, "0")  # Default tolerance
                self.entries[class_name][f"{field}_pos_tolerance"] = pos_tolerance_entry
                
                # Negative tolerance entry
                neg_tolerance_entry = ttk.Entry(frame, width=8, validate="key",
                                          validatecommand=(self.validate_numeric, '%P'))
                neg_tolerance_entry.grid(row=row, column=3, padx=5, pady=2)
                neg_tolerance_entry.insert(0, "0")  # Default tolerance
                self.entries[class_name][f"{field}_neg_tolerance"] = neg_tolerance_entry
        
        # Add Save button at bottom
        save_frame = ttk.Frame(self.class_values_tab)
        save_frame.pack(fill="x", pady=10)
        ttk.Button(save_frame, text="Save Class Values", command=self.save_all).pack()

    def update_tabs(self, *args):
        if self.apply_segmentation.get() and self.compare_values.get():
            if not self.class_values_tab:
                self.create_class_values_tab()
        else:
            if self.class_values_tab:
                self.notebook.forget(self.class_values_tab)
                self.class_values_tab = None
    
    def handle_segmentation_toggle(self):
        if not self.apply_segmentation.get():
            self.compare_values.set(False)
            self.compare_checkbox.configure(state='disabled')
        else:
            self.compare_checkbox.configure(state='normal')

    def load_values(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                # Convert from old format if needed
                if isinstance(next(iter(data.values()))[next(iter(self.fields))], (str, int, float)):
                    return {class_name: {field: str(value) 
                            for field, value in values.items()} 
                            for class_name, values in data.items()}
                return {class_name: {field: values[field]["value"] 
                        for field in self.fields} 
                        for class_name, values in data.items()}
        return {class_name: {field: "0" for field in self.fields} 
                for class_name in self.classes}
    
    def load_segmentation_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.apply_segmentation.set(settings.get("apply_segmentation", False))
                self.compare_values.set(settings.get("compare_values", False))
    
    def save_all(self):
        # Save segmentation settings
        settings = {
            "apply_segmentation": self.apply_segmentation.get(),
            "compare_values": self.compare_values.get()
        }
        
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        
        # Save class values and tolerances
        values = {}
        for class_name in self.classes:
            values[class_name] = {
                field: {
                    "value": self.entries[class_name][field].get(),
                    "pos_tolerance": self.entries[class_name][f"{field}_pos_tolerance"].get(),
                    "neg_tolerance": self.entries[class_name][f"{field}_neg_tolerance"].get()
                } for field in self.fields
            }
        
        with open(self.data_file, 'w') as f:
            json.dump(values, f, indent=4)
        
        print("All settings saved successfully")

    def validate_entry(self, value):
        """Validate that entry is a number or empty"""
        if value == "":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False


class RecordingSettingsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Recording Settings")
        self.settings_file = "recording_settings.json"
        
        # Initialize settings
        self.video_choice = tk.StringVar(value="None")
        self.image_choice = tk.StringVar(value="None")
        
        # Initialize exposure time settings
        self.et_mode = tk.StringVar(value="Fixed")  # "Fixed" or "Iterate"
        self.et_fixed = tk.StringVar(value="1000")  # Fixed exposure time in microseconds
        self.et_start = tk.StringVar(value="1000")  # Start of iteration range
        self.et_end = tk.StringVar(value="10000")   # End of iteration range
        self.et_step = tk.StringVar(value="1000")   # Step size for iteration
        
        # Add RSI mode setting
        self.rsi_mode = tk.StringVar(value="Manual")  # "Manual" or "RSI"
        
        self.load_settings()
        self.create_widgets()
    
    def load_settings(self):
        """Load existing settings from file"""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.video_choice.set(settings.get("video_recording", "None"))
                self.image_choice.set(settings.get("image_recording", "None"))
                # Load exposure time settings
                et_settings = settings.get("exposure_time", {})
                self.et_mode.set(et_settings.get("mode", "Fixed"))
                self.et_fixed.set(et_settings.get("fixed_value", "1000"))
                self.et_start.set(et_settings.get("start", "1000"))
                self.et_end.set(et_settings.get("end", "10000"))
                self.et_step.set(et_settings.get("step", "1000"))
                self.rsi_mode.set(settings.get("rsi_mode", "Manual"))
    
    def handle_video_selection(self):
        """When video is selected, disable image options"""
        if self.video_choice.get() != "None":
            self.image_choice.set("None")
    
    def handle_image_selection(self):
        """When image is selected, disable video options"""
        if self.image_choice.get() != "None":
            self.video_choice.set("None")
        
    def create_widgets(self):
        # Title for the window
        title_label = tk.Label(self.root, text="Recording Settings", font=("Arial", 14))
        title_label.pack(pady=10)

        # Record Videos Section
        video_frame = ttk.LabelFrame(self.root, text="Record Videos", padding="10")
        video_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Radiobutton(video_frame, text="None", variable=self.video_choice, 
                      value="None", command=self.handle_video_selection).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Radiobutton(video_frame, text="Raw Video", variable=self.video_choice, 
                      value="Raw Video", command=self.handle_video_selection).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        tk.Radiobutton(video_frame, text="Annotated Video", variable=self.video_choice, 
                      value="Annotated Video", command=self.handle_video_selection).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        tk.Radiobutton(video_frame, text="Both", variable=self.video_choice, 
                      value="Both", command=self.handle_video_selection).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        
        # Record Images Section
        image_frame = ttk.LabelFrame(self.root, text="Record Images", padding="10")
        image_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Radiobutton(image_frame, text="None", variable=self.image_choice, 
                      value="None", command=self.handle_image_selection).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Radiobutton(image_frame, text="Raw Image", variable=self.image_choice, 
                      value="Raw Image", command=self.handle_image_selection).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        tk.Radiobutton(image_frame, text="Annotated Image", variable=self.image_choice, 
                      value="Annotated Image", command=self.handle_image_selection).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        tk.Radiobutton(image_frame, text="Both", variable=self.image_choice, 
                      value="Both", command=self.handle_image_selection).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        
        # Exposure Time Section
        et_frame = ttk.LabelFrame(self.root, text="Exposure Time Settings", padding="10")
        et_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Mode selection
        mode_frame = ttk.Frame(et_frame)
        mode_frame.pack(fill="x", pady=5)
        ttk.Radiobutton(mode_frame, text="Fixed ET", variable=self.et_mode, 
                       value="Fixed", command=self.update_et_fields).pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="Iterate ET", variable=self.et_mode, 
                       value="Iterate", command=self.update_et_fields).pack(side="left", padx=5)

        # Fixed ET settings
        self.fixed_frame = ttk.Frame(et_frame)
        ttk.Label(self.fixed_frame, text="Fixed ET (μs):").pack(side="left", padx=5)
        ttk.Entry(self.fixed_frame, textvariable=self.et_fixed, width=10).pack(side="left", padx=5)

        # Iteration settings
        self.iter_frame = ttk.Frame(et_frame)
        ttk.Label(self.iter_frame, text="Start (μs):").grid(row=0, column=0, padx=5, pady=2)
        ttk.Entry(self.iter_frame, textvariable=self.et_start, width=10).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(self.iter_frame, text="End (μs):").grid(row=1, column=0, padx=5, pady=2)
        ttk.Entry(self.iter_frame, textvariable=self.et_end, width=10).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(self.iter_frame, text="Step (μs):").grid(row=2, column=0, padx=5, pady=2)
        ttk.Entry(self.iter_frame, textvariable=self.et_step, width=10).grid(row=2, column=1, padx=5, pady=2)

        self.update_et_fields()  # Show/hide appropriate fields based on initial mode
        
        # RSI Integration Section
        rsi_frame = ttk.LabelFrame(self.root, text="RSI Integration", padding="10")
        rsi_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Radiobutton(rsi_frame, text="Start recordings manually", 
                       variable=self.rsi_mode, value="Manual").pack(anchor="w", pady=5)
        ttk.Radiobutton(rsi_frame, text="Listen for RSI Signal", 
                       variable=self.rsi_mode, value="RSI").pack(anchor="w", pady=5)
        
        # Save Button
        save_button = tk.Button(self.root, text="Save Settings", command=self.save_settings)
        save_button.pack(pady=10)

    def update_et_fields(self):
        """Show/hide ET fields based on selected mode"""
        if self.et_mode.get() == "Fixed":
            self.iter_frame.pack_forget()
            self.fixed_frame.pack(fill="x", pady=5)
        else:
            self.fixed_frame.pack_forget()
            self.iter_frame.pack(fill="x", pady=5)

    def save_settings(self):
        settings = {
            "video_recording": self.video_choice.get(),
            "image_recording": self.image_choice.get(),
            "exposure_time": {
                "mode": self.et_mode.get(),
                "fixed_value": self.et_fixed.get(),
                "start": self.et_start.get(),
                "end": self.et_end.get(),
                "step": self.et_step.get()
            },
            "rsi_mode": self.rsi_mode.get()
        }
        
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        
        print("Recording Settings Saved:", settings)


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
        
        self.load_settings()
        self.create_widgets()
    
    def load_settings(self):
        settings = {}  # Initialize settings dictionary
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.show_boxes.set(settings.get("show_boxes", True))
                self.show_labels.set(settings.get("show_labels", True))
                # Load position settings
                positions = settings.get("label_positions", {"top-left": True})
                for pos, value in positions.items():
                    if pos in self.label_positions:
                        self.label_positions[pos].set(value)
                # Load bottom left fields
                bottom_left = settings.get("bottom_left_fields", {})
                for field, values in bottom_left.items():
                    if field in self.bottom_left_fields:
                        self.bottom_left_fields[field]["show"].set(values.get("show", False))
                        self.bottom_left_fields[field]["value"].set(values.get("value", ""))
                # Load bottom right fields
                bottom_right = settings.get("bottom_right_fields", {})
                for field, values in bottom_right.items():
                    if field in self.bottom_right_fields:
                        self.bottom_right_fields[field]["show"].set(values.get("show", False))
                        self.bottom_right_fields[field]["value"].set(values.get("value", ""))
                # Load top right fields
                top_right = settings.get("top_right_fields", {})
                for field, values in top_right.items():
                    # Only load fields that still exist in top_right_fields
                    if field in self.top_right_fields:
                        self.top_right_fields[field]["show"].set(values.get("show", False))
                        self.top_right_fields[field]["value"].set(values.get("value", ""))
                # Load top left fields
                top_left = settings.get("top_left_fields", {})
                for field, values in top_left.items():
                    if field in self.top_left_fields:
                        self.top_left_fields[field]["show"].set(values.get("show", False))
                        self.top_left_fields[field]["value"].set(values.get("value", ""))
        
        # Load ET from recording settings
        if os.path.exists(self.recording_settings_file):
            with open(self.recording_settings_file, 'r') as f:
                recording_settings = json.load(f)
                et_settings = recording_settings.get("exposure_time", {})
                if et_settings.get("mode") == "Fixed":
                    self.et_field["value"].set(et_settings.get("fixed_value", ""))
                else:
                    self.et_field["value"].set(f"{et_settings.get('start', '')}-{et_settings.get('end', '')}")
                self.et_field["show"].set(settings.get("show_et", False))
    
    def create_widgets(self):
        # Add Material Defaults section at the top
        material_frame = ttk.LabelFrame(self.root, text="Material Defaults", padding="10")
        material_frame.pack(fill="x", padx=10, pady=5, before=self.root.children[list(self.root.children.keys())[0]])
        
        # Create material selection frame
        materials = self.material_defaults.get_materials_list()
        if materials:
            ttk.Checkbutton(material_frame, text="Use Material Defaults",
                          variable=self.use_material_defaults,
                          command=self.handle_material_selection).pack(side="left", padx=5)
            
            self.material_menu = ttk.Combobox(material_frame, 
                                            textvariable=self.selected_material,
                                            values=materials,
                                            state='readonly')
            self.material_menu.pack(side="left", padx=5)
            self.material_menu.bind('<<ComboboxSelected>>', self.apply_material_defaults)
            
            if not self.use_material_defaults.get():
                self.material_menu.configure(state='disabled')
        else:
            ttk.Label(material_frame, text="No material defaults available. Add them in Material Defaults settings.").pack(padx=5, pady=5)
        
        # Label Position Frame with Subsections (removed Display Options section)
        position_frame = ttk.LabelFrame(self.root, text="Label Positions", padding="10")
        position_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Top Left Section with Fields
        top_left_frame = ttk.Frame(position_frame)
        top_left_frame.pack(fill="x", pady=5)
        ttk.Checkbutton(top_left_frame, text="Top Left", 
                       variable=self.label_positions["top-left"]).pack(anchor="w")
        
        # Top Left Options Subframe
        tl_options = ttk.LabelFrame(top_left_frame, text="Top Left Options", padding="5")
        tl_options.pack(fill="x", padx=20)
        
        # Add ET field first in Top Left Options
        field_frame = ttk.Frame(tl_options)
        field_frame.pack(fill="x", pady=2)
        ttk.Checkbutton(field_frame, text="ET",
                      variable=self.et_field["show"]).pack(side="left")
        et_entry = ttk.Entry(field_frame, textvariable=self.et_field["value"])
        et_entry.pack(side="right", fill="x", expand=True)
        et_entry.configure(state='readonly')  # Make ET field read-only
        
        # Add remaining top left fields
        for field_name, field_vars in self.top_left_fields.items():
            field_frame = ttk.Frame(tl_options)
            field_frame.pack(fill="x", pady=2)
            
            ttk.Checkbutton(field_frame, text=field_name,
                          variable=field_vars["show"]).pack(side="left")
            if "value" in field_vars:  # Only create entry for non-script-calculated fields
                entry = ttk.Entry(field_frame, textvariable=field_vars["value"])
                entry.pack(side="right", fill="x", expand=True)
        
        # Top Right Section with Additional Fields
        top_right_frame = ttk.Frame(position_frame)
        top_right_frame.pack(fill="x", pady=5)
        ttk.Checkbutton(top_right_frame, text="Top Right", 
                       variable=self.label_positions["top-right"]).pack(anchor="w")
        
        # Top Right Options Subframe
        tr_options = ttk.LabelFrame(top_right_frame, text="Top Right Options", padding="5")
        tr_options.pack(fill="x", padx=20)
        
        # Add fields to Top Right Options
        for field_name, field_vars in self.top_right_fields.items():
            field_frame = ttk.Frame(tr_options)
            field_frame.pack(fill="x", pady=2)
            
            ttk.Checkbutton(field_frame, text=field_name,
                          variable=field_vars["show"]).pack(side="left")
            if "value" in field_vars:  # Only create entry for user-input fields
                entry = ttk.Entry(field_frame, textvariable=field_vars["value"])
                entry.pack(side="right", fill="x", expand=True)
        
        # Bottom Left Section with Additional Fields
        bottom_left_frame = ttk.Frame(position_frame)
        bottom_left_frame.pack(fill="x", pady=5)
        ttk.Checkbutton(bottom_left_frame, text="Bottom Left", 
                       variable=self.label_positions["bottom-left"]).pack(anchor="w")
        
        # Bottom Left Options Subframe
        bl_options = ttk.LabelFrame(bottom_left_frame, text="Bottom Left Options", padding="5")
        bl_options.pack(fill="x", padx=20)
        
        # Add fields to Bottom Left Options
        for field_name, field_vars in self.bottom_left_fields.items():
            field_frame = ttk.Frame(bl_options)
            field_frame.pack(fill="x", pady=2)
            
            ttk.Checkbutton(field_frame, text=field_name,
                          variable=field_vars["show"]).pack(side="left")
            ttk.Entry(field_frame, textvariable=field_vars["value"]).pack(side="right", fill="x", expand=True)

        # Bottom Right Section with Camera Fields
        bottom_right_frame = ttk.Frame(position_frame)
        bottom_right_frame.pack(fill="x", pady=5)
        ttk.Checkbutton(bottom_right_frame, text="Bottom Right", 
                       variable=self.label_positions["bottom-right"]).pack(anchor="w")
        
        # Bottom Right Options Subframe
        br_options = ttk.LabelFrame(bottom_right_frame, text="Bottom Right Options", padding="5")
        br_options.pack(fill="x", padx=20)
        
        # Add camera fields to Bottom Right Options
        for field_name, field_vars in self.bottom_right_fields.items():
            field_frame = ttk.Frame(br_options)
            field_frame.pack(fill="x", pady=2)
            
            ttk.Checkbutton(field_frame, text=field_name,
                          variable=field_vars["show"]).pack(side="left")
            ttk.Entry(field_frame, textvariable=field_vars["value"]).pack(side="right", fill="x", expand=True)
        
        # Save Button
        ttk.Button(self.root, text="Save Settings", 
                  command=self.save_settings).pack(pady=10)
    
    def handle_material_selection(self):
        if self.use_material_defaults.get():
            self.material_menu.configure(state='readonly')
            if self.selected_material.get():
                self.apply_material_defaults()
        else:
            self.material_menu.configure(state='disabled')
    
    def apply_material_defaults(self, event=None):
        if not self.use_material_defaults.get():
            return
            
        material = self.selected_material.get()
        if not material:
            return
            
        values = self.material_defaults.get_material_values(material)
        
        # Apply values to all field groups
        for group, fields in values.items():
            if hasattr(self, group):
                group_fields = getattr(self, group)
                for field, field_values in fields.items():
                    if field in group_fields:
                        group_fields[field]['value'].set(field_values)
    
    def save_settings(self):
        settings = {
            "show_boxes": self.show_boxes.get(),
            "show_labels": self.show_labels.get(),
            "label_positions": {pos: var.get() for pos, var in self.label_positions.items()},
            "bottom_left_fields": {
                field: {
                    "show": vars["show"].get(),
                    "value": vars["value"].get()
                } for field, vars in self.bottom_left_fields.items()
            },
            "bottom_right_fields": {
                field: {
                    "show": vars["show"].get(),
                    "value": vars["value"].get()
                } for field, vars in self.bottom_right_fields.items()
            },
            "top_right_fields": {
                field: {
                    "show": vars["show"].get(),
                    "value": vars["value"].get()
                } for field, vars in self.top_right_fields.items()
            },
            "top_left_fields": {
                field: {
                    "show": vars["show"].get(),
                    "value": vars["value"].get()
                } for field, vars in self.top_left_fields.items()
            },
            "show_et": self.et_field["show"].get(),
            "material_defaults": {
                "enabled": self.use_material_defaults.get(),
                "selected": self.selected_material.get()
            }
        }
        
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        
        print("Annotation Settings Saved:", settings)
    
    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                # ...existing loading code...
                
                # Load material defaults settings
                material_defaults = settings.get("material_defaults", {})
                self.use_material_defaults.set(material_defaults.get("enabled", False))
                self.selected_material.set(material_defaults.get("selected", ""))
                
        # ...existing code...


class ImageDisplayFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.image_labels = {}
        self.current_layout = None
        self.settings_file = "recording_settings.json"
        
        # Define placeholder sizes
        self.placeholder_width = 640
        self.placeholder_height = 480
        
        self.setup_display()
        
    def setup_display(self):
        self.load_settings()
        self.create_image_labels()
        
    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = {"video_recording": "None", "image_recording": "None"}
            
    def create_image_labels(self):
        # Clear existing labels
        for widget in self.winfo_children():
            widget.destroy()
        self.image_labels = {}
        
        if self.settings["image_recording"] == "Both":
            # Create two frames side by side
            left_frame = ttk.LabelFrame(self, text="Raw Image")
            left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            
            right_frame = ttk.LabelFrame(self, text="Annotated Image")
            right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
            
            self.image_labels["raw"] = tk.Label(left_frame, 
                background='black', width=self.placeholder_width//2, height=self.placeholder_height//2)
            self.image_labels["raw"].pack(expand=True, fill="both", padx=2, pady=2)
            
            self.image_labels["annotated"] = tk.Label(right_frame,
                background='black', width=self.placeholder_width//2, height=self.placeholder_height//2)
            self.image_labels["annotated"].pack(expand=True, fill="both", padx=2, pady=2)
            
            # Configure grid weights
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)
            
        elif self.settings["image_recording"] in ["Raw Image", "Annotated Image"]:
            label_type = "raw" if self.settings["image_recording"] == "Raw Image" else "annotated"
            frame_title = "Raw Image" if label_type == "raw" else "Annotated Image"
            
            main_frame = ttk.LabelFrame(self, text=frame_title)
            main_frame.pack(expand=True, fill="both", padx=10, pady=10)
            
            self.image_labels[label_type] = tk.Label(main_frame,
                background='black', width=self.placeholder_width, height=self.placeholder_height)
            self.image_labels[label_type].pack(expand=True, fill="both", padx=2, pady=2)
        
        else:
            # Create a placeholder frame when no recording option is selected
            placeholder_frame = ttk.LabelFrame(self, text="No Recording Selected")
            placeholder_frame.pack(expand=True, fill="both", padx=10, pady=10)
            
            placeholder_label = tk.Label(placeholder_frame, text="Select recording options to view images",
                                       background='black', foreground='white')
            placeholder_label.pack(expand=True, fill="both", padx=2, pady=2)
            
    def update_image(self, image_type, image):
        """Update the display with new image(s)"""
        if image_type in self.image_labels:
            # Convert numpy array to PhotoImage and update label
            photo = ImageTk.PhotoImage(image=Image.fromarray(image))
            self.image_labels[image_type].configure(image=photo)
            self.image_labels[image_type].image = photo  # Keep reference

class GraphSettingsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Settings")
        self.settings_file = "graph_settings.json"
        
        # Define chart groups and their metrics
        self.chart_groups = {
            "X Position Values": ["X Average", "X Maximum", "X Minimum"],
            "Y Position Values": ["Y Average", "Y Maximum", "Y Minimum"],
            "Position Standard Deviations": ["X Average Standard Deviation", "Y Average Standard Deviation"],
            "Class Area": ["Class Area"],
            "Class Area Standard Deviation": ["Class Area Standard Deviation"]
        }
        
        # Initialize metrics and chart visibility
        self.metrics = {}
        self.show_charts = {}  # Track which charts to show during recording
        for group in self.chart_groups:
            self.show_charts[group] = tk.BooleanVar(value=False)
            for metric in self.chart_groups[group]:
                self.metrics[metric] = tk.BooleanVar(value=False)
        
        # Initialize save options
        self.save_charts = tk.BooleanVar(value=False)
        
        self.load_settings()
        self.create_widgets()
    
    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                for metric, value in settings.get("metrics", {}).items():
                    if metric in self.metrics:
                        self.metrics[metric].set(value)
                for chart, value in settings.get("show_charts", {}).items():
                    if chart in self.show_charts:
                        self.show_charts[chart].set(value)
                self.save_charts.set(settings.get("save_charts", False))
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(main_frame, text="Metrics and Chart Settings", font=("Arial", 12)).pack(pady=10)
        
        # Create sections for each chart group
        for group_name, group_metrics in self.chart_groups.items():
            group_frame = ttk.LabelFrame(main_frame, text=group_name, padding="5")
            group_frame.pack(fill="x", pady=5, padx=5)
            
            # Add chart visibility checkbox
            ttk.Checkbutton(group_frame, text="Show chart during recording",
                          variable=self.show_charts[group_name]).pack(anchor="w", pady=2, padx=5)
            
            ttk.Separator(group_frame, orient='horizontal').pack(fill='x', pady=5)
            
            # Add metrics checkboxes
            for metric in group_metrics:
                ttk.Checkbutton(group_frame, text=metric, 
                              variable=self.metrics[metric]).pack(anchor="w", pady=2, padx=20)
        
        # Save Options Section
        save_frame = ttk.LabelFrame(main_frame, text="Save Options", padding="5")
        save_frame.pack(fill="x", pady=10, padx=5)
        
        ttk.Checkbutton(save_frame, text="Save all charts after recording",
                       variable=self.save_charts).pack(anchor="w", pady=5)
        
        ttk.Button(main_frame, text="Save Settings",
                  command=self.save_settings).pack(pady=10)
    
    def save_settings(self):
        settings = {
            "metrics": {metric: var.get() for metric, var in self.metrics.items()},
            "show_charts": {chart: var.get() for chart, var in self.show_charts.items()},
            "save_charts": self.save_charts.get(),
            "chart_groups": self.chart_groups
        }
        
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        
        print("Graph Settings Saved:", settings)

class MainGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Welding Monitoring System")
        
        # Set fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.root.quit())
        
        # Add status message variable
        self.status_message = tk.StringVar(value="Ready to record...")
        
        # Add recording state
        self.is_recording = False
        
        # Configure grid
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_rowconfigure(1, weight=1)  # For image display
        main_container.grid_rowconfigure(2, weight=0)  # For status bar
        main_container.grid_columnconfigure(0, weight=1)
        
        # Create control panel frame with distinctive styling
        control_frame = ttk.LabelFrame(main_container, text="Control Panel")
        control_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Left side buttons
        left_button_frame = ttk.Frame(control_frame)
        left_button_frame.pack(side="left", fill="y")
        
        class_value_button = ttk.Button(left_button_frame, text="Segmentation Settings", 
                                     command=self.open_segmentation_and_class_gui)
        class_value_button.pack(side="left", padx=5, pady=5)
        
        recording_settings_button = ttk.Button(left_button_frame, text="Recording Settings", 
                                            command=self.open_recording_settings_gui)
        recording_settings_button.pack(side="left", padx=5, pady=5)
        
        annotation_settings_button = ttk.Button(left_button_frame, text="Annotation Settings", 
                                              command=self.open_annotation_settings_gui)
        annotation_settings_button.pack(side="left", padx=5, pady=5)
        
        graph_settings_button = ttk.Button(left_button_frame, text="Graph Settings",
                                        command=self.open_graph_settings_gui)
        graph_settings_button.pack(side="left", padx=5, pady=5)
        
        # Add material defaults button after graph settings button
        material_defaults_button = ttk.Button(left_button_frame, text="Material Defaults",
                                          command=self.open_material_defaults_gui)
        material_defaults_button.pack(side="left", padx=5, pady=5)
        
        # Center the record button
        record_frame = ttk.Frame(control_frame)
        record_frame.pack(side="left", fill="both", expand=True, padx=20)
        
        self.record_button = tk.Button(record_frame, text="Start Recording", 
                                     command=self.toggle_recording,
                                     font=("Arial", 14, "bold"),
                                     bg="green", fg="white",
                                     height=2)
        self.record_button.pack(expand=True)
        
        # Right side exit button
        exit_button = ttk.Button(control_frame, text="Exit", command=self.root.quit)
        exit_button.pack(side="right", padx=5, pady=5)
        
        # Create and add image display frame
        self.display_frame = ImageDisplayFrame(main_container)
        self.display_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Add status bar
        status_frame = ttk.Frame(main_container)
        status_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=2)
        status_label = ttk.Label(status_frame, textvariable=self.status_message)
        status_label.pack(side="left", padx=5)
    
    def toggle_recording(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.record_button.config(text="Stop Recording", bg="red")
            self.status_message.set("Recording in progress...")
        else:
            self.record_button.config(text="Start Recording", bg="green")
            self.status_message.set("Recording stopped.")
    
    def update_status(self, message, is_warning=False):
        """Update the status message bar. Use is_warning=True for threshold alerts."""
        self.status_message.set(message)
        
    def update_display(self, raw_image=None, annotated_image=None):
        """Update the display with new images"""
        if raw_image is not None:
            self.display_frame.update_image("raw", raw_image)
        if annotated_image is not None:
            self.display_frame.update_image("annotated", annotated_image)
    
    def open_recording_settings_gui(self):
        # Create a new window for the Class Value GUI
        recording_setting_window = tk.Toplevel(self.root)
        app = RecordingSettingsGUI(recording_setting_window)
    
    def open_segmentation_and_class_gui(self):
        settings_window = tk.Toplevel(self.root)
        app = SegmentationAndClassGUI(settings_window)
        
    def open_annotation_settings_gui(self):
        annotation_settings_window = tk.Toplevel(self.root)
        app = AnnotationSettingsGUI(annotation_settings_window)
        
    def open_graph_settings_gui(self):
        graph_settings_window = tk.Toplevel(self.root)
        app = GraphSettingsGUI(graph_settings_window)
        
    def open_material_defaults_gui(self):
        defaults_window = tk.Toplevel(self.root)
        from material_defaults_gui import MaterialDefaultsGUI
        app = MaterialDefaultsGUI(defaults_window)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = MainGUI(root)
    root.mainloop()
