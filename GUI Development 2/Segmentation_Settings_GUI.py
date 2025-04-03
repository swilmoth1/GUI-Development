import tkinter as tk
from tkinter import ttk
import json
import os
import customtkinter as ctk

class SegmentationSettingsGUI:
    def __init__(self, root):
        self.root = root
        # Create settings window
        self.window = ctk.CTkToplevel(root)
        self.window.title("Segmentation Settings")
        
        # Set up window close protocol
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Prevent interaction with main window while open
        self.window.grab_set()
        
        # Add title
        title = ctk.CTkLabel(self.window, text="Segmentation Settings", 
                            font=("Arial", 20, "bold"))
        title.pack(pady=20)

        # Create tabview
        self.tabview = ctk.CTkTabview(self.window)
        self.tabview.pack(expand=True, fill="both", padx=20, pady=20)

        # Create tabs
        self.seg_settings_tab = self.tabview.add("Segmentation Settings")
        self.class_values_tab = self.tabview.add("Class Values and Tolerances")

        # Setup initial variables
        self.setup_variables()
        self.load_settings()  # Load saved settings if they exist
        
        # Initialize tabs
        self.init_segmentation_tab()
        self.init_class_values_tab()

    def setup_variables(self):
        self.classes = ["Welding Wire", "Solidification Zone", "Arc Flash"]
        self.fields = [
            "x_min", "x_max", "y_min", "y_max", "y_average", "x_average", 
            "area_average", "area_std_deviation", "y_avg_std_deviation", "x_avg_std_deviation"
        ]
        self.data_file = "class_values.json"
        self.settings_file = "segmentation_settings.json"
        self.materials_file = "material_presets.json"  # New file for material presets
        
        # Segmentation settings
        self.apply_segmentation = ctk.BooleanVar(master=self.window, value=False)
        self.compare_values = ctk.BooleanVar(master=self.window, value=False)
        
        # Initialize empty values
        self.default_values = {}
        self.comparative_values = {}
        self.entries = {}

    def load_values(self):
        """Load values from JSON file or create default structure"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading values: {e}")
        
        # Create and save default structure if file doesn't exist or has error
        default_values = {}
        for class_name in self.classes:
            default_values[class_name] = {
                field: {
                    "value": "0",
                    "pos_tolerance": "0",
                    "neg_tolerance": "0"
                } for field in self.fields
            }
        
        # Save default values
        try:
            with open(self.data_file, 'w') as f:
                json.dump(default_values, f, indent=4)
        except Exception as e:
            print(f"Error saving default values: {e}")
        
        return default_values

    def save_class_values(self):
        """Save class values to JSON file"""
        values_dict = {}
        for class_name in self.classes:
            values_dict[class_name] = {}
            for field in self.fields:
                values_dict[class_name][field] = {
                    "value": self.entries[class_name][field].get() or "0",
                    "pos_tolerance": self.entries[class_name][f"{field}_pos_tolerance"].get() or "0",
                    "neg_tolerance": self.entries[class_name][f"{field}_neg_tolerance"].get() or "0"
                }
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(self.data_file)), exist_ok=True)
            
            # Save to file
            with open(self.data_file, 'w') as f:
                json.dump(values_dict, f, indent=4)
            
            print(f"Values saved successfully to {self.data_file}")
            self.window.destroy()  # Destroy the window
        except Exception as e:
            print(f"Error saving class values: {e}")

    def init_segmentation_tab(self):
        settings_frame = ctk.CTkFrame(self.seg_settings_tab)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add checkboxes with simplified configuration
        self.seg_checkbox = ctk.CTkCheckBox(
            master=settings_frame, 
            text="Apply segmentation model",
            command=self.toggle_compare_checkbox,
            variable=self.apply_segmentation
        )
        self.seg_checkbox.pack(anchor="w", padx=20, pady=10)
        
        self.compare_checkbox = ctk.CTkCheckBox(
            master=settings_frame, 
            text="Compare values to class value settings",
            variable=self.compare_values,
            state="disabled"
        )
        self.compare_checkbox.pack(anchor="w", padx=20, pady=10)

        # Add save button
        save_button = ctk.CTkButton(
            master=settings_frame,
            text="Save Settings",
            command=self.save_settings,
            font=("Arial", 12, "bold")
        )
        save_button.pack(anchor="w", padx=20, pady=20)

    def toggle_compare_checkbox(self):
        if self.apply_segmentation.get():
            self.compare_checkbox.configure(state="normal")
        else:
            self.compare_values.set(False)
            self.compare_checkbox.configure(state="disabled")

    def save_settings(self):
        settings = {
            "apply_segmentation": self.apply_segmentation.get(),
            "compare_values": self.compare_values.get()
        }
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
                self.window.destroy()  # Destroy the window
        except Exception as e:
            print(f"Error saving settings: {e}")
            # Could add error message display here
            

    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.apply_segmentation.set(settings.get("apply_segmentation", False))
                self.compare_values.set(settings.get("compare_values", False))
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is invalid, use defaults
            self.apply_segmentation.set(False)
            self.compare_values.set(False)

    def validate_entry(self, value):
        """Validate numeric entry"""
        if value == "" or value == "-":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False

    def load_preset(self, selected_preset):
        """Load values from selected material preset"""
        try:
            with open(self.materials_file, 'r') as f:
                materials = json.load(f)
                if selected_preset in materials:
                    preset_data = materials[selected_preset]
                    class_name = self.class_tabs.get()
                    if class_name in self.entries:
                        for field in self.fields:
                            if field in preset_data:
                                self.entries[class_name][field].delete(0, 'end')
                                self.entries[class_name][field].insert(0, preset_data[field].get("value", "0"))
                                self.entries[class_name][f"{field}_pos_tolerance"].delete(0, 'end')
                                self.entries[class_name][f"{field}_pos_tolerance"].insert(0, preset_data[field].get("pos_tolerance", "0"))
                                self.entries[class_name][f"{field}_neg_tolerance"].delete(0, 'end')
                                self.entries[class_name][f"{field}_neg_tolerance"].insert(0, preset_data[field].get("neg_tolerance", "0"))
        except Exception as e:
            print(f"Error loading material preset: {e}")

    def save_as_material_preset(self):
        """Save current values as a material preset"""
        dialog = ctk.CTkInputDialog(text="Enter material name:", title="Save Material Preset")
        material_name = dialog.get_input()
        if material_name:
            try:
                # Load existing materials or create new dict
                try:
                    with open(self.materials_file, 'r') as f:
                        materials = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    materials = {}
                
                # Save current values as material preset
                materials[material_name] = {}
                class_name = self.class_tabs.get()
                if class_name in self.entries:
                    materials[material_name] = {
                        field: {
                            "value": self.entries[class_name][field].get(),
                            "pos_tolerance": self.entries[class_name][f"{field}_pos_tolerance"].get(),
                            "neg_tolerance": self.entries[class_name][f"{field}_neg_tolerance"].get()
                        } for field in self.fields
                    }
                
                with open(self.materials_file, 'w') as f:
                    json.dump(materials, f, indent=4)
                
                # Update preset menu
                self.update_preset_menu()
            except Exception as e:
                print(f"Error saving material preset: {e}")

    def update_preset_menu(self):
        """Update the preset menu with available materials"""
        try:
            with open(self.materials_file, 'r') as f:
                materials = json.load(f)
                preset_names = list(materials.keys())
        except (FileNotFoundError, json.JSONDecodeError):
            preset_names = []
        
        self.preset_menu.configure(values=preset_names)

    def init_class_values_tab(self):
        # Create main frame for class values
        main_frame = ctk.CTkFrame(self.class_values_tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add preset selection at the top
        preset_frame = ctk.CTkFrame(main_frame)
        preset_frame.pack(fill="x", padx=10, pady=5)
        
        preset_label = ctk.CTkLabel(preset_frame, text="Load Preset:", font=("Arial", 12, "bold"))
        preset_label.pack(side="left", padx=5)
        
        # Initialize empty preset menu
        self.preset_var = ctk.StringVar(value="Select Material")
        self.preset_menu = ctk.CTkOptionMenu(
            preset_frame,
            values=[],  # Start with empty list
            command=self.load_preset,
            variable=self.preset_var
        )
        self.preset_menu.pack(side="left", padx=5)
        
        # Add save as material preset button
        save_preset_button = ctk.CTkButton(
            preset_frame,
            text="Save as Material Preset",
            command=self.save_as_material_preset,
            font=("Arial", 12)
        )
        save_preset_button.pack(side="right", padx=5)
        
        # Update preset menu with any existing materials
        self.update_preset_menu()

        # Create nested tabview for classes
        self.class_tabs = ctk.CTkTabview(main_frame)
        self.class_tabs.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Initialize entries dictionary
        self.entries = {}
        saved_values = self.load_values()
        
        # Create tab for each class
        for class_name in self.classes:
            tab = self.class_tabs.add(class_name)
            self.entries[class_name] = {}
            
            # Create scrollable frame for this class
            scroll_frame = ctk.CTkScrollableFrame(tab)
            scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Add headers
            headers = ["Field", "Value", "+Tolerance", "-Tolerance"]
            for col, header in enumerate(headers):
                label = ctk.CTkLabel(scroll_frame, text=header, font=("Arial", 12, "bold"))
                label.grid(row=0, column=col, padx=5, pady=5, sticky='w')
            
            # Add fields for this class
            for row, field in enumerate(self.fields, start=1):
                field_label = ctk.CTkLabel(scroll_frame, text=field)
                field_label.grid(row=row, column=0, padx=5, pady=2, sticky='w')
                
                # Get saved values with defaults
                field_data = saved_values.get(class_name, {}).get(field, {})
                value = field_data.get("value", "0")
                pos_tol = field_data.get("pos_tolerance", "0")
                neg_tol = field_data.get("neg_tolerance", "0")
                
                # Create entries
                value_entry = ctk.CTkEntry(scroll_frame, width=100)
                value_entry.grid(row=row, column=1, padx=5, pady=2)
                value_entry.insert(0, value)
                self.entries[class_name][field] = value_entry
                
                pos_tol_entry = ctk.CTkEntry(scroll_frame, width=80)
                pos_tol_entry.grid(row=row, column=2, padx=5, pady=2)
                pos_tol_entry.insert(0, pos_tol)
                self.entries[class_name][f"{field}_pos_tolerance"] = pos_tol_entry
                
                neg_tol_entry = ctk.CTkEntry(scroll_frame, width=80)
                neg_tol_entry.grid(row=row, column=3, padx=5, pady=2)
                neg_tol_entry.insert(0, neg_tol)
                self.entries[class_name][f"{field}_neg_tolerance"] = neg_tol_entry
        
        # Add Save button
        save_button = ctk.CTkButton(
            main_frame,
            text="Save Class Values",
            command=self.save_class_values,
            font=("Arial", 12, "bold")
        )
        save_button.pack(pady=10)

    def on_closing(self):
        """Handle window closing"""
        self.window.grab_release()  # Release the grab before destroying
        self.window.destroy()  # Destroy the window
