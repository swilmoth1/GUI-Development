import tkinter as tk
import customtkinter as ctk
import json
import os
import numpy as np
from tkinter import ttk

class GraphSettingsGUI:
    def __init__(self, root):
        self.root = root
        self.window = ctk.CTkToplevel(root)
        self.window.title("Graph Settings")
        self.graph_settings_file = "graph_settings.json"
        
        #Define chart groups and their metrics
        self.chart_groups = {
            "X Position Values": ["X Average", "X Maximum", "X Minimum"],
            "Y Position Values": ["Y Average", "Y Maximum", "Y Minimum"],
            "Position Standard Deviations": ["X Average Standard Deviation", "Y Average Standard Deviation"],
            "Class Area": ["Class Area"],
            "Class Area Standard Deviation": ["Class Area Standard Deviation"]
        }
        #prevent interaction with the main GUI window while open
        self.window.grab_set()
        # Initialize metrics and chart visibility
        self.metrics= {}
        self.show_charts = {}
        for group in self.chart_groups:
            self.show_charts[group] = tk.BooleanVar(value=False)
            for metric in self.chart_groups[group]:
                self.metrics[metric] = tk.BooleanVar(value=False)
                
        # Initialize save options
        self.save_charts = tk.BooleanVar(value=False)
        
        self.load_settings()
        self.create_widgets()
        
    def load_settings(self):
        if os.path.exists(self.graph_settings_file):
            with open(self.graph_settings_file, 'r') as f:
                settings=json.load(f)
                for metric, value in settings.get("metrics", {}).items():
                    if metric in self.metrics:
                        self.metrics[metric].set(value)
                for chart, value in settings.get("show_charts", {}).items():
                    if chart in self.show_charts:
                        self.show_charts[chart].set(value)
                self.save_charts.set(settings.get("save_charts",False))
                
    def create_widgets(self):
        # Create main frame without padding arguments
        main_frame = ctk.CTkFrame(self.window)
        
        # Use grid instead of pack since parent uses grid
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add weight to grid configuration
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(main_frame, text="Metrics and Chart Settings", font=("Arial",12)).pack(pady=10)
        
        # Create sections for each chart group
        for group_name, group_metrics in self.chart_groups.items():
            group_frame = ctk.CTkFrame(main_frame)
            group_frame_name = ctk.CTkLabel(group_frame,text=group_name)
            group_frame_name.pack()
            group_frame.pack(fill="x", pady=5,padx=5)
            
            ctk.CTkCheckBox(group_frame, text="Show chart during recording",
                            variable=self.show_charts[group_name]).pack(anchor="w", pady=2, padx=5)

            ttk.Separator(group_frame, orient='horizontal').pack(fill='x',pady=5)
            
            # Add metrics checkboxes
            for metric in group_metrics:
                ctk.CTkCheckBox(group_frame, text=metric, variable=self.metrics[metric]).pack(anchor="w",pady=2,padx=20)
                
        # Save Options Selection
        save_frame = ctk.CTkFrame(main_frame)
        save_frame_label = ctk.CTkLabel(save_frame, text="Save Options", padx=5, pady=5)
        save_frame_label.pack()
        save_frame.pack(fill="x",pady=5,padx=5)
        
        ctk.CTkCheckBox(save_frame, text="Save all charts after recording", variable=self.save_charts).pack(anchor="w",pady=5)
        
        ctk.CTkButton(main_frame, text="Save Settings", command=self.save_settings).pack(pady=10)
        
    def save_settings(self):
        settings = {
            "metrics": {metric: var.get() for metric, var in self.metrics.items()},
            "show_charts": {chart: var.get() for chart, var in self.show_charts.items()},
            "save_charts": self.save_charts.get(),
            "chart_groups": self.chart_groups
        }
        
        with open(self.graph_settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        
        print("Graph Settings Saved:", settings)
        self.on_closing()


    def on_closing(self):
        """Properly cleanup widgets and destroy window"""
        # Release grab before destroying
        self.window.grab_release()
        
        
        
        # Destroy window
        if self.window.winfo_exists():
            self.window.destroy()