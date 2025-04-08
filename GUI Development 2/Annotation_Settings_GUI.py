import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math
import os
import json
import Material_Defaults_GUI as MDG

class AnnotationSettingsGUI:
    def __init__(self, root):
        self.root = root
        
        # Create settings window with proper cleanup handling
        self.window = ctk.CTkToplevel(root)
        self.window.title("Annotation Settings")
        self.window.after(10, self.window.lift)  # Ensure window appears on top
        self.window.grab_set()
        
        # Store widget references for proper cleanup
        self.widgets = []
        
        #setup window closing protocol
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        #prevent interaction with the main GUI window while open
        self.window.grab_set()
        
        # Add title to Recording Settings window
        title = ctk.CTkLabel(self.window, text="Annotation Settings", 
                            font=("Arial", 20, "bold"))
        title.grid(row=0,column=0,pady=20)
        
        
        self.material_defaults_file = "material_defaults.json"
        self.recording_settings_file = "recording_settings.json"
        self.settings_file = "annotation_settings.json"
        
        # Add material defaults
        self.material_defaults = MDG.MaterialDefaultsGUI.load_materials(self)
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
        
        
        
        self.load_settings(None)  # Initialize with no material selected
        self.create_widgets()
        
    

    def create_widgets(self):
        # Material Selection Section
        material_frame = ctk.CTkFrame(self.window)
        self.widgets.append(material_frame)
        material_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        material_label = ctk.CTkLabel(material_frame, text="Material Default Selection")
        material_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        materials = self.load_defaults()
        
       
        if materials:
            use_defaults_cb = ctk.CTkCheckBox(material_frame, 
                                             text="Use Material Defaults", 
                                             variable=self.use_material_defaults,
                                             command=self.handle_material_selection)
            use_defaults_cb.grid(row=1, column=0, padx=5)
            
            self.material_menu = ctk.CTkComboBox(material_frame,
                                                values=list(materials.keys()),
                                                command=self.apply_material_defaults_and_draw_notebook)
            

            self.material_menu.grid(row=1, column=1, padx=5)
            self.material_menu.set("Select Material")
            
            self.update_material_menu_button = ctk.CTkButton(
                material_frame, 
                text="Update Annotation Settings", 
                command=lambda: self.apply_material_defaults_and_draw_notebook(None)
            )
            self.update_material_menu_button.grid(row=1, column=2, padx=5)
            
            
            if not self.use_material_defaults.get():
                self.material_menu.configure(state="disabled")
        
      
        
        self.draw_annotation_setting_notebook()
        
        # Save Button
        save_button = ctk.CTkButton(self.window, text="Save Settings", command=self.save_settings)
        self.widgets.append(save_button)
        save_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        # Configure grid weights
        self.window.grid_rowconfigure(2, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

    def apply_material_defaults_and_draw_notebook(self, choice=None):
        # print(choice)
        # material_selection_from_combobox=self.load_material_from_json(choice)
        self.load_settings(choice)
        self.draw_annotation_setting_notebook()
    
    def load_material_from_json(self, choice=None):
        with open(self.material_defaults_file, 'r') as f:
            data=json.load(f)
            material_settings_from_selection = data.get(choice)
            return material_settings_from_selection
        
        
        
    def draw_annotation_setting_notebook(self):
        try:
            settings_notebook.forget()
        except NameError:
            pass
    
        settings_notebook = ttk.Notebook(self.window)
        self.widgets.append(settings_notebook)
        settings_notebook.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        
        settings_frame = ctk.CTkFrame(settings_notebook)
        self.widgets.append(settings_frame)
        settings_notebook.add(settings_frame, text="Annotation Settings")
        corners = ["Top Left", "Top Right", "Bottom Left", "Bottom Right"]
        for i, corner in enumerate(corners):
            corner_frame = ctk.CTkFrame(settings_frame)
            self.widgets.append(corner_frame)
            corner_frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew")
            
            # Get the field dictionary for this corner
            field_dict = getattr(self, f"{corner.lower().replace(' ', '_')}_fields")
            
            # Store corner checkbox reference with command to update children
            corner_var = self.label_positions[corner.lower().replace(" ", "-")]
            corner_checkbox = ctk.CTkCheckBox(
                corner_frame, 
                text=corner, 
                variable=corner_var,
                command=lambda d=field_dict: self.update_child_checkboxes(d, corner_var)
            )
            corner_checkbox.grid(row=0, column=0)
            
            # Field selection frame
            fields_frame = ctk.CTkFrame(corner_frame)
            self.widgets.append(fields_frame)
            fields_frame.grid(row=1, column=0, padx=5, pady=5)
            
            # Add appropriate fields based on corner
            for row, (field, vars) in enumerate(field_dict.items()):
                child_checkbox = ctk.CTkCheckBox(
                    fields_frame, 
                    text=field, 
                    variable=vars["show"],
                    command=lambda c=corner_var, d=field_dict: self.update_parent_checkbox(c, d)
                )
                child_checkbox.grid(row=row, column=0)
                
                if "value" in vars:
                    ctk.CTkEntry(fields_frame, textvariable=vars["value"]).grid(row=row, column=1)

    def update_child_checkboxes(self, field_dict, parent_var):
        """Update child checkboxes based on parent state"""
        parent_state = parent_var.get()
        for field_vars in field_dict.values():
            field_vars["show"].set(parent_state)

    def update_parent_checkbox(self, corner_var, field_dict):
        """Update parent checkbox based on children states"""
        any_checked = False
        all_unchecked = True
        
        for field_vars in field_dict.values():
            if field_vars["show"].get():
                any_checked = True
                all_unchecked = False
                break
        
        if any_checked:
            corner_var.set(True)
        elif all_unchecked:
            corner_var.set(False)

    def save_settings(self):
        # Get current material
        material = self.material_menu.get()
        
        # Create settings dictionary
        settings = {
            "material_defaults": {
                "enabled": self.use_material_defaults.get(),
                "selected": material
            },
            "manual_settings": {
                "show_boxes": self.show_boxes.get(),
                "show_labels": self.show_labels.get(),
                "label_positions": {pos: var.get() for pos, var in self.label_positions.items()},
                "top_left_fields": {field: {"show": vars["show"].get(), "value": vars.get("value", tk.StringVar()).get()} 
                                  for field, vars in self.top_left_fields.items()},
                "top_right_fields": {field: {"show": vars["show"].get(), "value": vars.get("value", tk.StringVar()).get()} 
                                   for field, vars in self.top_right_fields.items()},
                "bottom_left_fields": {field: {"show": vars["show"].get(), "value": vars.get("value", tk.StringVar()).get()} 
                                     for field, vars in self.bottom_left_fields.items()},
                "bottom_right_fields": {field: {"show": vars["show"].get(), "value": vars.get("value", tk.StringVar()).get()} 
                                      for field, vars in self.bottom_right_fields.items()}
            }
        }
        
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        
        self.on_closing()

    def apply_material_defaults(self, choice=None):
        """Apply settings when material is selected from dropdown"""
        if not self.use_material_defaults.get():
            return
            
        material = self.material_menu.get()
        if material == "Select Material":
            return
            
        # Load material defaults
        defaults = self.load_defaults()
        if material not in defaults:
            return
            
        material_settings = defaults[material]
        
        # Clear existing settings
        self.clear_settings()
        
        # Apply new settings
        for key, value in material_settings.items():
            if key == "label_positions":
                for pos, enabled in value.items():
                    if pos in self.label_positions:
                        self.label_positions[pos].set(enabled)
                        
            elif key in ["top_left_fields", "top_right_fields", 
                        "bottom_left_fields", "bottom_right_fields"]:
                field_group = getattr(self, key)
                for field, settings in value.items():
                    if field in field_group:
                        if isinstance(settings, dict):
                            field_group[field]["show"].set(settings.get("show", False))
                            if "value" in field_group[field]:
                                field_group[field]["value"].set(settings.get("value", ""))
        
        # Force complete UI refresh
        self.refresh_ui()
    
    def clear_settings(self):
        """Reset all settings to defaults"""
        for group in [self.top_left_fields, self.top_right_fields, 
                     self.bottom_left_fields, self.bottom_right_fields]:
            for field in group.values():
                field["show"].set(False)
                if "value" in field:
                    field["value"].set("")
    
    def refresh_ui(self):
        """Force complete UI refresh"""
        self.window.update_idletasks()
        self.window.update()
        
        # Trigger update on all frames
        for widget in self.widgets:
            if widget.winfo_exists():
                widget.update()
                
        self.draw_annotation_setting_notebook()
        
        

    def load_settings(self, weld_material=None):
        if os.path.exists(self.material_defaults_file):
            with open(self.material_defaults_file, 'r') as f:
                settings = json.load(f)
                if weld_material and weld_material in settings:
                    self._apply_settings(settings[weld_material])
                elif settings:  # If no specific material, use first available
                    first_material = next(iter(settings))
                    self._apply_settings(settings[first_material])

    def _apply_settings(self, settings_branch):
        """Helper method to apply settings from a specific branch"""
        try:
            # Set basic flags
            self.show_boxes.set(settings_branch.get("show_boxes", True))
            self.show_labels.set(settings_branch.get("show_labels", True))
            
            # Update label positions
            for pos, value in settings_branch.get("label_positions", {}).items():
                if pos in self.label_positions:
                    self.label_positions[pos].set(value)
            
            # Define field mappings
            field_mappings = {
                "bottom_left_fields": self.bottom_left_fields,
                "bottom_right_fields": self.bottom_right_fields,
                "top_right_fields": self.top_right_fields,
                "top_left_fields": self.top_left_fields
            }
            
            # Update each field group
            for group_name, fields in field_mappings.items():
                if group_data := settings_branch.get(group_name, {}):
                    for field_name, field_vars in fields.items():
                        if field_data := group_data.get(field_name):
                            # Update show/hide status
                            if isinstance(field_data, dict):
                                field_vars["show"].set(field_data.get("show", False))
                                if "value" in field_vars and "value" in field_data:
                                    field_vars["value"].set(str(field_data["value"]))
                            else:
                                # Handle direct value assignment
                                if "value" in field_vars:
                                    field_vars["value"].set(str(field_data))
                                field_vars["show"].set(True)
                                    
        except Exception as e:
            print(f"Error applying settings: {e}")
            
        # Force update of all widgets
        self.window.update_idletasks()

    def on_closing(self):
        """Properly cleanup widgets and destroy window"""
        # Release grab before destroying
        self.window.grab_release()
        
        # Clean up widgets
        for widget in self.widgets:
            if widget.winfo_exists():
                widget.destroy()
        self.widgets.clear()
        
        # Destroy window
        if self.window.winfo_exists():
            self.window.destroy()

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
        material=event
        values = self.load_defaults()
        
        # Apply values to all field groups
        for group, fields in values.items():
            if hasattr(self,group):
                group_fields = getattr(self, group)
                for field, field_values in fields.items():
                    if field in group_fields:
                        group_fields[field]['value'].set(field_values)
    
    
    
    def load_defaults(self):
        if os.path.exists(self.material_defaults_file):
            with open(self.material_defaults_file, 'r') as f:
                return json.load(f)
        return {}
        
    def update_gui(display_frame):
        if display_frame:
            display_frame.load_settings()
            display_frame.update_display([])
            display_frame.update_idletasks()