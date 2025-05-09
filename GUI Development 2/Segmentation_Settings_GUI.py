import tkinter as tk
from tkinter import ttk
import json
import os
import customtkinter as ctk
import easygui

class SegmentationSettingsGUI:
    
    
    def __init__(self, root, callback=None):
        self.root = root
        self.callback = callback
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
        
        # Load available presets at initialization
        self.available_presets = self.get_available_presets()
        
        # Initialize tabs
        self.init_segmentation_tab()
        self.init_class_values_tab()
    
    def update_heat_input(self):
        try:
            current = float(self.metadata_entries["Current (A)"].get())
            voltage = float(self.metadata_entries["Voltage (V)"].get())
            travel_speed_in_min = float(self.metadata_entries["Travel Speed (in/min)"].get())
            travel_speed_mm_s = travel_speed_in_min * 0.4233  # 1 in/min = 0.4233 mm/s
            if travel_speed_mm_s > 0:
                heat_input = (current * voltage) / travel_speed_mm_s * 0.8
                self.metadata_entries["Heat Input (J/mm)"].configure(state="normal")
                self.metadata_entries["Heat Input (J/mm)"].delete(0, tk.END)
                self.metadata_entries["Heat Input (J/mm)"].insert(0, f"{heat_input:.2f}")
                self.metadata_entries["Heat Input (J/mm)"].configure(state="disabled")
        except ValueError:
            # Incomplete or invalid input, just skip update
            self.metadata_entries["Heat Input (J/mm)"].configure(state="normal")
            self.metadata_entries["Heat Input (J/mm)"].delete(0, tk.END)
            self.metadata_entries["Heat Input (J/mm)"].configure(state="disabled")
    
    def load_preset(self, selected_preset):
        """Load values from selected material preset"""
        try:
            with open(self.data_file, 'r') as f:
                materials = json.load(f)
                if selected_preset in materials:
                    # Update material entry
                    self.material_entry.delete(0, 'end')
                    self.material_entry.insert(0, selected_preset)
                    
                    # Get preset data for the selected material
                    preset_data = materials[selected_preset]
                    
                    # Update values for each class and field
                    for class_name in self.classes:
                        if class_name in preset_data:  # Check if class exists in preset
                            class_data = preset_data[class_name]
                            for field in self.fields:
                                if field in class_data:  # Check if field exists in class data
                                    # Update value
                                    self.entries[class_name][field].delete(0, 'end')
                                    self.entries[class_name][field].insert(0, class_data[field]["value"])
                                    
                                    # Update tolerances
                                    self.entries[class_name][f"{field}_pos_tolerance"].delete(0, 'end')
                                    self.entries[class_name][f"{field}_pos_tolerance"].insert(0, class_data[field]["pos_tolerance"])
                                    
                                    self.entries[class_name][f"{field}_neg_tolerance"].delete(0, 'end')
                                    self.entries[class_name][f"{field}_neg_tolerance"].insert(0, class_data[field]["neg_tolerance"])
                    
                    print(f"Successfully loaded preset: {selected_preset}")
                else:
                    print(f"Preset {selected_preset} not found")
        except Exception as e:
            print(f"Error loading material preset: {e}")

    def save_as_material_preset(self):
        """Save current values as a material preset"""
        material_name = self.material_entry.get().strip()
        if not material_name:
            print("Please enter a material name")
            return
            
        try:
            # Load existing materials or create new dict
            try:
                with open(self.data_file, 'r') as f:
                    materials = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                materials = {}
            
            # Save current values as material preset
            materials[material_name] = {}
            for class_name in self.classes:
                if class_name in self.entries:
                    for field in self.fields:
                        if field not in materials[material_name]:
                            materials[material_name][field] = {}
                        materials[material_name][field] = {
                            "value": self.entries[class_name][field].get(),
                            "pos_tolerance": self.entries[class_name][f"{field}_pos_tolerance"].get(),
                            "neg_tolerance": self.entries[class_name][f"{field}_neg_tolerance"].get()
                        }
            
            with open(self.data_file, 'w') as f:
                json.dump(materials, f, indent=4)
            
            # Update preset menu
            self.update_preset_menu()
            # Set the current selection to the saved material
            self.preset_var.set(material_name)
            
        except Exception as e:
            print(f"Error saving material preset: {e}")



    def update_preset_menu(self):
        """Update the preset menu with available materials"""
        try:
            # Get fresh list of presets
            preset_names = self.get_available_presets()
            
            # Update the menu with current presets
            if preset_names:
                self.preset_menu.configure(values=preset_names)
                if self.preset_var.get() not in preset_names:
                    self.preset_var.set(preset_names[0])
            else:
                self.preset_menu.configure(values=["No presets available"])
                self.preset_var.set("No presets available")
                
        except Exception as e:
            print(f"Error updating preset menu: {e}")
    
    def init_class_values_tab(self):
        # Create main frame for class values
        main_frame = ctk.CTkFrame(self.class_values_tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add preset selection at the top
        preset_frame = ctk.CTkFrame(main_frame)
        preset_frame.pack(fill="x", padx=10, pady=5)
        
        # Use grid for preset selection
        preset_label = ctk.CTkLabel(preset_frame, text="Load Preset:", font=("Arial", 12, "bold"))
        preset_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.preset_var = ctk.StringVar(value="Select Material")
        initial_values = self.available_presets if self.available_presets else ["No presets available"]
        self.preset_menu = ctk.CTkOptionMenu(
            preset_frame,
            values=initial_values,
            command=self.load_preset,
            variable=self.preset_var
        )
        self.preset_menu.grid(row=0, column=1, padx=5, pady=5)
        
        # Material Selection section using grid
        material_selection_frame = ctk.CTkFrame(main_frame)
        material_selection_frame.pack(fill="x", padx=10, pady=5)
        
        material_selection_label = ctk.CTkLabel(material_selection_frame, 
                                                text="Material:", 
                                                font=("Arial", 12, "bold"))
        material_selection_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.material_entry = ctk.CTkEntry(material_selection_frame, width=100)
        self.material_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        save_preset_button = ctk.CTkButton(
            material_selection_frame,
            text="Save as Material Preset",
            command=self.save_as_material_preset,
            font=("Arial", 12)
        )
        save_preset_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        # Configure grid weights
        material_selection_frame.grid_columnconfigure(1, weight=1)

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
        self.callback()
        save_button.pack(pady=10)
    def on_closing(self):
        """Handle window closing"""
        self.window.grab_release()  # Release the grab before destroying
        self.window.destroy()  # Destroy the window

    def toggle_excel_metadata_state(self):
        state = "normal" if self.save_excel_var.get() else "disabled"
        for key, entry in self.metadata_entries.items():
            if key in self.disabled_keys:
                continue  # Keep exposure fields always disabled
            entry.configure(state=state)

    def toggle_compare_checkbox(self):
        if self.apply_segmentation.get():
            self.compare_checkbox.configure(state="normal")
        else:
            self.compare_values.set(False)
            self.compare_checkbox.configure(state="disabled")
    
    def save_settings(self):
        settings = {
            "apply_segmentation": bool(self.apply_segmentation.get()),
            "compare_values": bool(self.compare_values.get()),
            "segmentation_file": str(self.segmentation_file.get()),
            "save_raw_excel": self.save_excel_var.get()
        }

        # Always save metadata
        metadata = {}
        for key, entry in self.metadata_entries.items():
            entry.configure(state="normal")
            metadata[key] = entry.get()
            if key in self.disabled_keys:
                entry.configure(state="disabled")

        # ✅ Add checkbox state to metadata
        metadata["Save Raw Data in Excel"] = self.save_excel_var.get()

        try:
            with open("raw_experiment_excel_data.json", "w") as f:
                json.dump(metadata, f, indent=4)
        except Exception as e:
            print(f"Error saving metadata: {e}")

        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            self.window.destroy()
        except Exception as e:
            print(f"Error saving settings: {e}")




    def validate_entry(self, value):
        """Validate numeric entry"""
        if value == "" or value == "-":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def load_settings(self):
        """Load segmentation-specific settings"""
        try:
            if not os.path.exists(self.settings_file):
                return  # Use default values if file doesn't exist
                
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                
            # Load all settings
            if "apply_segmentation" in settings:
                self.apply_segmentation.set(bool(settings["apply_segmentation"]))
            if "compare_values" in settings:
                self.compare_values.set(bool(settings["compare_values"]))
            if "segmentation_file" in settings:
                self.segmentation_file.set(settings["segmentation_file"])
            if "raw_experiment_excel_data" in settings:
                self.raw_experiment_excel_data.set(settings["raw_experiment_excel_data"])
                
        except Exception as e:
            print(f"Error loading segmentation settings: {e}")
            # Keep default values on error
        
    def get_available_presets(self):
        """Get list of available presets from class_values.json"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    materials = json.load(f)
                    return list(materials.keys())
        except Exception as e:
            print(f"Error loading presets: {e}")
        return []
    
    def setup_variables(self):
        self.classes = ["Welding Wire", "Solidification Zone", "Arc Flash"]
        self.fields = [
            "x_min", "x_max", "y_min", "y_max", "y_average", "x_average", 
            "area_average", "area_std_deviation", "y_avg_std_deviation", "x_avg_std_deviation"
        ]
        self.data_file = "class_values.json"
        self.settings_file = "segmentation_settings.json"
        
        # Initialize all possible settings attributes
        self.apply_segmentation = ctk.BooleanVar(master=self.window, value=False)
        self.compare_values = ctk.BooleanVar(master=self.window, value=False)
        self.compare_checkbox = None  # Will be initialized later in init_segmentation_tab
        
        # Initialize empty values
        self.default_values = {}
        self.comparative_values = {}
        self.entries = {}
        
        # Setup Segmentation Best File
        self.segmentation_file = ctk.StringVar(value="")

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
        self.segmentation_file.set(f.get('segmentation_file', False))
        # Save default values
        try:
            with open(self.data_file, 'w') as f:
                json.dump(default_values, f, indent=4)
        except Exception as e:
            print(f"Error saving default values: {e}")
        
        return default_values

    def save_class_values(self):
        """Save class values to JSON file"""
        material_name = self.material_entry.get().strip()
        if not material_name:
            print("Please enter a material name")
            return
            
        try:
            # Load existing materials first
            existing_materials = {}
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    existing_materials = json.load(f)
            
            # Add new material values to existing ones
            existing_materials[material_name] = {}
            for class_name in self.classes:
                existing_materials[material_name][class_name] = {}
                for field in self.fields:
                    existing_materials[material_name][class_name][field] = {
                        "value": self.entries[class_name][field].get() or "0",
                        "pos_tolerance": self.entries[class_name][f"{field}_pos_tolerance"].get() or "0",
                        "neg_tolerance": self.entries[class_name][f"{field}_neg_tolerance"].get() or "0"
                    }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(self.data_file)), exist_ok=True)
            
            # Save all materials back to file
            with open(self.data_file, 'w') as f:
                json.dump(existing_materials, f, indent=4)
            
            print(f"Values saved successfully to {self.data_file}")
            if self.callback:
                self.callback()
            self.window.destroy()
        except Exception as e:
            print(f"Error saving class values: {e}")

    def get_segmentation_file(self):
        file_path = easygui.fileopenbox(
            title="Select Segmentation Model File",
            default="*.pt",  # Optional: filter for PyTorch model files
            filetypes=["*.pt", "*.*"]
        )
        if file_path:
            self.segmentation_file.set(file_path)

    def init_segmentation_tab(self):
        settings_frame = ctk.CTkFrame(self.seg_settings_tab)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Add checkboxes
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

        # Segmentation file selection
        file_frame = ctk.CTkFrame(settings_frame)
        file_frame.pack(fill="x", padx=20, pady=10)

        file_label = ctk.CTkLabel(file_frame, text="Segmentation File:")
        file_label.pack(side="left", padx=5)

        file_path_label = ctk.CTkLabel(file_frame, textvariable=self.segmentation_file)
        file_path_label.pack(side="left", padx=5, fill="x", expand=True)

        select_file_btn = ctk.CTkButton(
            file_frame,
            text="Select File",
            command=self.get_segmentation_file,
            width=100
        )
        select_file_btn.pack(side="right", padx=5)

        # Save Excel checkbox
        self.save_excel_var = tk.BooleanVar(value=False)
        self.save_excel_checkbox = ctk.CTkCheckBox(
            master=settings_frame,
            text="Save Raw Data in Excel",
            variable=self.save_excel_var,
            command=self.toggle_excel_metadata_state
        )
        self.save_excel_checkbox.pack(anchor="w", padx=20, pady=10)

        # Metadata fields
        self.metadata_frame = ctk.CTkFrame(settings_frame)
        self.metadata_frame.pack(fill="both", padx=20, pady=10)

        self.metadata_entries = {}
        self.disabled_keys = [
            "Starting Exposure Time (μs)", "Ending Exposure Time (μs)", "Increment (μs)",
            "Exposure Time (μs)", "Heat Input (J/mm)"
        ]

        self.metadata_fields = [
            "Segmentation Type", "Starting Exposure Time (μs)",
            "Ending Exposure Time (μs)", "Increment (μs)", "Exposure Time (μs)", "Filter Applied",
            "Material", "Job Number", "Wire Feed Speed (in/min)", "Travel Speed (in/min)",
            "Camera Model", "Lens Model", "Illumination", "Viewing Angle",
            "Shielding Gas", "Current (A)", "Voltage (V)", "Heat Input (J/mm)", "CTWD (mm)"
        ]

        for label in self.metadata_fields:
            row = ctk.CTkFrame(self.metadata_frame)
            row.pack(fill="x", pady=2)
            lbl = ctk.CTkLabel(row, text=label, width=180, anchor="w")
            lbl.pack(side="left")
            entry = ctk.CTkEntry(row, width=300)
            entry.pack(side="left")
            if label in self.disabled_keys:
                entry.configure(state="disabled")
            self.metadata_entries[label] = entry

        # Load existing metadata and recording settings
        self.load_metadata_from_json()

        # Hook up dynamic heat input calculation
        self.metadata_entries["Travel Speed (in/min)"].bind("<KeyRelease>", lambda e: self.update_heat_input())
        self.metadata_entries["Current (A)"].bind("<KeyRelease>", lambda e: self.update_heat_input())
        self.metadata_entries["Voltage (V)"].bind("<KeyRelease>", lambda e: self.update_heat_input())

        # Save button
        save_button = ctk.CTkButton(
            master=settings_frame,
            text="Save Settings",
            command=self.save_settings,
            font=("Arial", 12, "bold")
        )
        save_button.pack(anchor="w", padx=20, pady=20)
    
    def load_metadata_from_json(self):
    # Load experiment metadata if it exists
        try:
            with open("raw_experiment_excel_data.json", "r") as f:
                data = json.load(f)
            for key, entry in self.metadata_entries.items():
                if key in data:
                    entry.configure(state="normal")
                    entry.delete(0, tk.END)
                    entry.insert(0, data[key])
                    if key in self.disabled_keys:
                        entry.configure(state="disabled")
            self.save_excel_var.set(data.get("Save Raw Data in Excel", False))

            self.update_heat_input()
        except FileNotFoundError:
            pass  # No saved metadata yet

        # Load exposure time settings from recording_settings.json
        try:
            with open("recording_settings.json", "r") as f:
                recording_settings = json.load(f)

            et_mode = recording_settings.get("et_mode", "Fixed")

            if et_mode == "Fixed":
                self.metadata_entries["Starting Exposure Time (μs)"].configure(state="normal")
                self.metadata_entries["Ending Exposure Time (μs)"].configure(state="normal")
                self.metadata_entries["Increment (μs)"].configure(state="normal")
                self.metadata_entries["Exposure Time (μs)"].configure(state="normal")

                self.metadata_entries["Starting Exposure Time (μs)"].delete(0, tk.END)
                self.metadata_entries["Ending Exposure Time (μs)"].delete(0, tk.END)
                self.metadata_entries["Increment (μs)"].delete(0, tk.END)
                self.metadata_entries["Exposure Time (μs)"].delete(0, tk.END)

                self.metadata_entries["Starting Exposure Time (μs)"].insert(0, "N/A")
                self.metadata_entries["Ending Exposure Time (μs)"].insert(0, "N/A")
                self.metadata_entries["Increment (μs)"].insert(0, "N/A")
                self.metadata_entries["Exposure Time (μs)"].insert(0, recording_settings.get("et_fixed", ""))

            elif et_mode == "Iterate":
                self.metadata_entries["Starting Exposure Time (μs)"].configure(state="normal")
                self.metadata_entries["Ending Exposure Time (μs)"].configure(state="normal")
                self.metadata_entries["Increment (μs)"].configure(state="normal")
                self.metadata_entries["Exposure Time (μs)"].configure(state="normal")

                self.metadata_entries["Starting Exposure Time (μs)"].delete(0, tk.END)
                self.metadata_entries["Ending Exposure Time (μs)"].delete(0, tk.END)
                self.metadata_entries["Increment (μs)"].delete(0, tk.END)
                self.metadata_entries["Exposure Time (μs)"].delete(0, tk.END)

                self.metadata_entries["Starting Exposure Time (μs)"].insert(0, recording_settings.get("et_start", ""))
                self.metadata_entries["Ending Exposure Time (μs)"].insert(0, recording_settings.get("et_end", ""))
                self.metadata_entries["Increment (μs)"].insert(0, recording_settings.get("et_step", ""))
                self.metadata_entries["Exposure Time (μs)"].insert(0, "Filled during iteration")  # Will be filled during iteration

            # Re-disable fields after filling
            for key in ["Starting Exposure Time (μs)", "Ending Exposure Time (μs)", "Increment (μs)", "Exposure Time (μs)"]:
                self.metadata_entries[key].configure(state="disabled")

        except FileNotFoundError:
            print("recording_settings.json not found.")
    
    















