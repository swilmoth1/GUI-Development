import tkinter as tk
from tkinter import ttk
import json
import os

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
        self.comparative_values = self.load_values()
        self.validate_numeric = self.root.register(self.validate_entry)
        self.entries = {}
        self.load_segmentation_settings()
        
        # Create main notebook for all tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Create tabs
        self.create_segmentation_tab()
        self.class_values_tab = None
        
        # Bind the segmentation settings change to update tabs
        self.apply_segmentation.trace('w', self.update_tabs)
        self.compare_values.trace('w', self.update_tabs)

        self.last_values = {}  # Store last values for comparison

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
                if isinstance(next(iter(data.values()))[next(iter(self.fields))], dict):
                    return {class_name: {field: values[field]["value"] 
                            for field in self.fields} 
                            for class_name, values in data.items()}
                return data
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
        
        self.check_tolerances()  # Check tolerances after saving
        
        print("All settings saved successfully")

    def check_tolerances(self):
        """Check if any values exceed their tolerances"""
        for class_name in self.classes:
            for field in self.fields:
                try:
                    value = float(self.entries[class_name][field].get())
                    pos_tol = float(self.entries[class_name][f"{field}_pos_tolerance"].get())
                    neg_tol = float(self.entries[class_name][f"{field}_neg_tolerance"].get())
                    
                    if 'last_values' not in self.__dict__:
                        self.last_values = {}
                    
                    if class_name not in self.last_values:
                        self.last_values[class_name] = {}
                    
                    if field not in self.last_values[class_name]:
                        self.last_values[class_name][field] = value
                        continue
                    
                    last_value = self.last_values[class_name][field]
                    if value > last_value + pos_tol or value < last_value - neg_tol:
                        self.root.master.show_alert(
                            f"Alert: {class_name} {field} value ({value}) exceeds tolerance range "
                            f"({last_value-neg_tol:.2f} to {last_value+pos_tol:.2f})"
                        )
                    else:
                        self.root.master.clear_alert()
                        
                    self.last_values[class_name][field] = value
                except ValueError:
                    continue

    def validate_entry(self, value):
        """Validate that entry is a number or empty"""
        if value == "":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False