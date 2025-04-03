import tkinter as tk
from tkinter import ttk
import json
import os

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