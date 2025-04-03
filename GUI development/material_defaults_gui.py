import tkinter as tk
from tkinter import ttk
from material_defaults import MaterialDefaults

class MaterialDefaultsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Material Defaults Settings")
        
        self.material_defaults = MaterialDefaults()
        self.current_material = tk.StringVar()
        self.fields = {
            'bottom_left_fields': ['Material', 'Job Number', 'Wire Feed Speed', 'Travel Speed'],
            'bottom_right_fields': ['Camera', 'Lens', 'Viewing Angle', 'Focus', 'Aperature', 'Distance', 'CTWD (mm)'],
            'top_right_fields': ['Illum', 'Shielding Gas', 'Note'],
            'top_left_fields': ['FA']
        }
        self.create_widgets()
    
    def create_widgets(self):
        # Material selection/creation frame
        material_frame = ttk.LabelFrame(self.root, text="Materials", padding="10")
        material_frame.pack(fill="x", padx=10, pady=5)
        
        # Material selection
        ttk.Label(material_frame, text="Select Material:").pack(side="left", padx=5)
        self.material_menu = ttk.Combobox(material_frame, textvariable=self.current_material,
                                        values=self.material_defaults.get_materials_list())
        self.material_menu.pack(side="left", padx=5)
        self.material_menu.bind('<<ComboboxSelected>>', self.load_material_values)
        
        # New material entry
        ttk.Label(material_frame, text="New Material:").pack(side="left", padx=5)
        self.new_material_entry = ttk.Entry(material_frame)
        self.new_material_entry.pack(side="left", padx=5)
        ttk.Button(material_frame, text="Add Material", 
                  command=self.add_material).pack(side="left", padx=5)
        
        # Settings notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.entries = {}
        for section, fields in self.fields.items():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=section.replace('_', ' ').title())
            
            self.entries[section] = {}
            for field in fields:
                field_frame = ttk.Frame(frame)
                field_frame.pack(fill="x", pady=2)
                ttk.Label(field_frame, text=field).pack(side="left", padx=5)
                entry = ttk.Entry(field_frame)
                entry.pack(side="right", fill="x", expand=True, padx=5)
                self.entries[section][field] = entry
        
        # Save button
        ttk.Button(self.root, text="Save Material Defaults", 
                  command=self.save_material).pack(pady=10)
    
    def add_material(self):
        new_material = self.new_material_entry.get().strip()
        if new_material:
            self.material_defaults.add_material(new_material, {})
            self.new_material_entry.delete(0, tk.END)
            self.refresh_materials()
    
    def refresh_materials(self):
        self.material_menu['values'] = self.material_defaults.get_materials_list()
    
    def load_material_values(self, event=None):
        material = self.current_material.get()
        if material:
            values = self.material_defaults.get_material_values(material)
            for section, fields in self.entries.items():
                for field, entry in fields.items():
                    entry.delete(0, tk.END)
                    entry.insert(0, values.get(section, {}).get(field, ""))
    
    def save_material(self):
        material = self.current_material.get()
        if material:
            values = {}
            for section, fields in self.entries.items():
                values[section] = {field: entry.get() for field, entry in fields.items()}
            self.material_defaults.add_material(material, values)
            print(f"Saved defaults for {material}")
            self.root.destroy()
