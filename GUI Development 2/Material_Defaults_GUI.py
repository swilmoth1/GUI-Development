import tkinter as tk
import json
import os
import customtkinter as ctk
from customtkinter import CTk

class MaterialDefaultsGUI:
    def __init__(self, root):
        self.root = root
        self.settings_file = "material_defaults.json"
        
        # Create material settings window
        self.window = ctk.CTkToplevel(root)
        self.window.title("Material Defaults")
        
        # Set up window close protocol
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Prevent interaction with main window while open
        self.window.grab_set()
        
        # Set fields
        self.fields = {
            'bottom_left_fields': ['Job Number', 'Wire Feed Speed', 'Travel Speed'],
            'bottom_right_fields': ['Camera', 'Lens', 'Viewing Angle', 'Focus', 'Aperature', 'Distance', 'CTWD (mm)'],
            'top_right_fields': ['Illum', 'Shielding Gas', 'Note'],
            'top_left_fields': ['FA']
        }
        self.current_material=tk.StringVar()
        
        # Add title
        title = ctk.CTkLabel(self.window, text="Material Defaults", 
                            font=("Arial", 20, "bold"))
        title.pack(pady=20)
        
        # Initialize empty materials dictionary
        self.materials = {}
        
        # Load materials before creating widgets
        self.load_materials()
        self.create_widgets()
    

    
    # Load any materials that might be stored in a .json file. Saved previously or one may not exist
    def load_materials(self):
        """Load materials from JSON file or create new one"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as file:
                    self.materials = json.load(file)
            else:
                # Create new file with empty dictionary
                self.materials = {}
                with open(self.settings_file, 'w') as file:
                    json.dump(self.materials, file, indent=4)
        except Exception as e:
            print(f"Error loading materials: {e}")
            self.materials = {}

    def save_materials(self):
        """Save materials to JSON file"""
        try:
            with open(self.settings_file, 'w') as file:
                json.dump(self.materials, file, indent=4)
        except Exception as e:
            print(f"Error saving materials: {e}")
        
    def create_widgets(self):
        # Material selection/creation frame
        material_frame = ctk.CTkFrame(master=self.window)
        material_frame.pack(fill="x", padx=10, pady=5)
        
        # Material frame label
        material_frame_label = ctk.CTkLabel(material_frame, text="Materials", font=("Arial", 16, "bold"))
        material_frame_label.pack(pady=10)
        
        self.current_material = tk.StringVar()
        
        # Material Selection
        ctk.CTkLabel(material_frame, text="Select Material:").pack(side="left", padx=5)
        self.material_menu = ctk.CTkOptionMenu(
                                                master=material_frame, 
                                                variable=self.current_material,  # Correctly assigned
                                                values=list(self.materials.keys()),  # Pass as a list
                                                command=self.load_material_values)  # No parentheses
        self.material_menu.pack(side="left", padx=5)
        
        # Material entry. Same frame.
        ctk.CTkLabel(material_frame, text="New Material:").pack(side="left", padx=5)
        self.new_material_entry = ctk.CTkEntry(material_frame)
        self.new_material_entry.pack(side="left", padx=5)
        
        # Add a save button for the new material
        ctk.CTkButton(material_frame, text="Add Material", command=self.add_material).pack(side="left", padx=5)
        
        # Add remove material button
        ctk.CTkButton(material_frame, text="Remove Material", command=self.remove_material).pack(side="left", padx=5)
        
        # Create a main content frame to hold tabs and their content
        main_content = ctk.CTkFrame(self.window)
        main_content.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create tab buttons frame inside main content
        self.tab_buttons_frame = ctk.CTkFrame(main_content)
        self.tab_buttons_frame.pack(fill="x", padx=10, pady=10)
        
        # Create buttons for each "tab"
        self.tab_buttons = {}
        for i, (section, fields) in enumerate(self.fields.items()):
            tab_button = ctk.CTkButton(self.tab_buttons_frame, text=section.replace('_', ' ').title(), 
                                       command=lambda i=i: self.switch_tab(i))
            tab_button.pack(side="left", padx=5)
            self.tab_buttons[section] = tab_button
        
        # Create the content frames (similar to notebook tabs)
        self.tab_content_frames = {}
        self.entries = {}  # Initialize entries dictionary
        for section, fields in self.fields.items():
            tab_content_frame = ctk.CTkFrame(main_content)
            self.tab_content_frames[section] = tab_content_frame
            self.entries[section] = {}  # Initialize section dictionary
            for field in fields:
                # Create frame for each entry
                field_frame = ctk.CTkFrame(tab_content_frame)
                field_frame.pack(fill="x", pady=2)
                
                # Create label for each entry
                field_frame_label = ctk.CTkLabel(field_frame, text=field)
                field_frame_label.pack(side="left", padx=5)
                
                # Create entry for each entry
                entry = ctk.CTkEntry(field_frame)
                entry.pack(side="right", fill="x", expand=True, padx=5)
                self.entries[section][field] = entry  # Store entry widget reference
                
            # Initially hide all content frames
            tab_content_frame.pack_forget()
        
        # Create bottom frame for save button (always visible)
        bottom_frame = ctk.CTkFrame(self.window)
        bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        # Add save button to bottom frame
        save_button = ctk.CTkButton(bottom_frame, text="Save Material Defaults", 
                                  command=self.save_materials_and_close)
        save_button.pack(pady=10)
        
        # Switch to the first tab by default
        self.switch_tab(0)
        
        
    def switch_tab(self, index):
        # Hide all tab content frames
        for frame in self.tab_content_frames.values():
            frame.pack_forget()
        
        # Show the selected tab content frame
        section = list(self.fields.keys())[index]
        self.tab_content_frames[section].pack(fill="both", padx=10, pady=10)
        
        
    def add_material(self, event=None):
        new_material = self.new_material_entry.get().strip()
        if new_material:
            self.materials[new_material] = {}  # Initialize with empty dict
            for section in self.fields.keys():
                self.materials[new_material][section] = {}
            self.save_defaults()
            self.new_material_entry.delete(0, tk.END)
            self.refresh_materials()  # This will now update the menu and select the new material

    def add_material2(self, name, values):
        self.materials[name] = values
        self.save_defaults()
        
    def save_defaults(self):
        with open(self.settings_file, "w") as f:
            json.dump(self.materials, f, indent=4)
            
    def refresh_materials(self):
        materials = list(self.materials.keys())
        self.material_menu.configure(values=materials)  # Update the available options
        if materials:  # If there are materials in the list
            self.material_menu.set(materials[-1])  # Set to the most recently added material
            self.current_material.set(materials[-1])  # Update the StringVar
        
    def load_material_values(self, event=None):
        material = self.current_material.get()
        if material and material in self.materials:
            values = self.materials[material]
            # Clear and update all entries
            for section, fields in self.entries.items():
                for field, entry in fields.items():
                    entry.delete(0, tk.END)
                    if section in values and field in values[section]:
                        entry.insert(0, values[section][field])
                
            
    def save_materials_and_close(self, event=None):
        material = self.current_material.get()
        if material:
            # Save current values
            self.materials[material] = {}
            for section, fields in self.entries.items():
                self.materials[material][section] = {}
                for field, entry in fields.items():
                    self.materials[material][section][field] = entry.get()
        
        self.save_defaults()
        self.on_closing()

    def remove_material(self, event=None):
        material = self.current_material.get()
        if material and material in self.materials:
            del self.materials[material]
            self.save_defaults()
            materials = list(self.materials.keys())
            self.material_menu.configure(values=materials)
            if materials:  # If there are still materials left
                self.material_menu.set(materials[0])  # Set to first material
                self.current_material.set(materials[0])
                self.load_material_values()  # Load the values of the newly selected material
            else:  # If no materials left
                self.material_menu.set("")
                self.current_material.set("")
                # Clear all entry fields
                for section, fields in self.entries.items():
                    for entry in fields.values():
                        entry.delete(0, tk.END)

    # Setup closing function
    def on_closing(self):
        self.window.grab_release()  # Release the grab
        self.window.destroy()  # Close the window