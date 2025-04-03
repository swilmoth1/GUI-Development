import tkinter as tk
from tkinter import ttk
import json
import os
from material_defaults import MaterialDefaults
from .update_gui import update_gui

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
        
        # Load material defaults settings
        material_defaults = settings.get("material_defaults", {})
        self.use_material_defaults.set(material_defaults.get("enabled", False))
        self.selected_material.set(material_defaults.get("selected", ""))
    
    def create_widgets(self):
        # Create material selection frame first without the 'before' parameter
        material_frame = ttk.LabelFrame(self.root, text="Material Defaults", padding="10")
        material_frame.pack(fill="x", padx=10, pady=5)
        
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
        """Save annotation settings to file"""
        settings = {}
        
        # Properly handle annotation variables
        for key, var in self.vars.items():
            if isinstance(var, dict):
                settings[key] = {
                    "enabled": var.get("enabled", tk.BooleanVar()).get(),
                    "threshold": var.get("threshold", tk.StringVar()).get()
                }
            else:
                settings[key] = var.get()
        
        # Save to file
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        
        # Update main GUI
        if hasattr(self.root, 'master') and hasattr(self.root.master, 'display_frame'):
            display_frame = self.root.master.display_frame
            update_gui(display_frame)
        
        print("Annotation Settings Saved:", settings)
        self.root.destroy()