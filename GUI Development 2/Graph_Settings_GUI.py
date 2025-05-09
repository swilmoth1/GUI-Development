import tkinter as tk
import customtkinter as ctk
import json
import os
import numpy as np
from tkinter import ttk
import easygui

class GraphSettingsGUI:
    def __init__(self, root,callback=None):
        self.root = root
        self.window = ctk.CTkToplevel(root)
        self.callback = callback
        self.window.title("Graph Settings")
        self.graph_settings_file = "graph_settings.json"
        self.save_folder=os.getcwd()
        self.setup_variables()
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
        
    def setup_variables(self):
        self.save_folder = tk.StringVar()
        # Initialize frame counts and settings
        self.metric_frame_counts = {}
        self.frame_counts_settings = {}
        # Initialize settings dictionaries
        self.show_charts_settings = {}
        self.metrics_settings = {}
        
    def load_settings(self):
        # Default settings structure
        default_settings = {
            "metrics": {
                "X Average": False,
                "X Maximum": False,
                "X Minimum": False,
                "Y Average": False,
                "Y Maximum": False,
                "Y Minimum": False,
                "X Average Standard Deviation": False,
                "Y Average Standard Deviation": False,
                "Class Area": False,
                "Class Area Standard Deviation": False
            },
            "show_charts": {
                "X Position Values": False,
                "Y Position Values": False,
                "Position Standard Deviations": False,
                "Class Area": False,
                "Class Area Standard Deviation": False
            },
            "save_charts": False,
            "save_folder": "",
            "frame_counts": {}
        }

        try:
            if os.path.exists(self.graph_settings_file):
                with open(self.graph_settings_file, 'r') as f:
                    settings = json.load(f)
                    
                    # Merge loaded settings with defaults
                    for category in default_settings:
                        if category in settings:
                            if isinstance(default_settings[category], dict):
                                default_settings[category].update(settings[category])
                            else:
                                default_settings[category] = settings[category]
                    
                    settings = default_settings
            else:
                settings = default_settings

            # Update GUI elements with settings
            for metric, value in settings["metrics"].items():
                if metric in self.metrics:
                    self.metrics[metric].set(value)

            for chart_group, value in settings["show_charts"].items():
                if chart_group in self.show_charts:
                    self.show_charts[chart_group].set(value)

            self.save_charts.set(settings.get("save_charts", False))
            self.save_folder = settings.get("save_folder", "")
            self.frame_counts_settings = settings.get("frame_counts", {})

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            # Use default settings if JSON is invalid
            settings = default_settings
        except Exception as e:
            print(f"Unexpected error loading settings: {e}")
            settings = default_settings
        
    def create_widgets(self):
        self.frame_counts = {}

        # Main frames for left and right columns
        main_frame = ctk.CTkFrame(self.window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        value_frame = ctk.CTkFrame(self.window)
        value_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(main_frame, text="Metrics and Chart Settings", font=("Arial", 12)).pack(pady=10)
        ctk.CTkLabel(value_frame, text="Frame Count Settings", font=("Arial", 12)).pack(pady=10)

        for group_name, group_metrics in self.chart_groups.items():
            # Left frame: checkboxes
            group_frame = ctk.CTkFrame(main_frame)
            ctk.CTkLabel(group_frame, text=group_name).pack()
            group_frame.pack(fill="x", pady=5, padx=5)

            # Show chart checkbox with saved setting
            current_value = False
            if group_name in self.show_charts:
                current_value = self.show_charts[group_name].get()
            show_var = ctk.BooleanVar(value=current_value)
            self.show_charts[group_name] = show_var
            ctk.CTkCheckBox(group_frame, text="Show chart during recording", variable=show_var).pack(anchor="w", pady=2, padx=5)

            ttk.Separator(group_frame, orient='horizontal').pack(fill='x', pady=5)

            for metric in group_metrics:
                # Metric checkbox with saved setting
                metric_var = ctk.BooleanVar(value=self.metrics.get(metric).get() if metric in self.metrics else False)
                self.metrics[metric] = metric_var
                ctk.CTkCheckBox(group_frame, text=metric, variable=metric_var).pack(anchor="w", pady=2, padx=20)

                # Right frame: frame count entry
                metric_frame = ctk.CTkFrame(value_frame)
                metric_frame.pack(fill="x", pady=2, padx=10)

                label_text = f"{metric} Frame Count"
                ctk.CTkLabel(metric_frame, text=label_text).pack(side="left", padx=5)

                # Default frame count value if present
                entry_value = self.frame_counts_settings.get(metric, "")
                entry_var = tk.StringVar(value=entry_value)
                entry = ctk.CTkEntry(metric_frame, width=60, textvariable=entry_var)
                entry.pack(side="right", padx=5)

                self.metric_frame_counts[metric] = entry_var

        # Save options
        save_frame = ctk.CTkFrame(main_frame)
        ctk.CTkLabel(save_frame, text="Save Options", padx=5, pady=5).pack()
        save_frame.pack(fill="x", pady=5, padx=5)
        ctk.CTkCheckBox(save_frame, text="Save all charts after recording", variable=self.save_charts).pack(anchor="w", pady=5)

        # Save location
        # save_location_frame = ctk.CTkFrame(main_frame)
        # ctk.CTkLabel(save_location_frame, text="Save Location", padx=5, pady=5).pack()
        # save_location_frame.pack(fill="x", pady=5, padx=5)
        # ctk.CTkButton(save_location_frame, text="Select Save Location", command=self.select_save_location).pack(pady=10)

        # Save Settings Button
        save_button_frame = ctk.CTkFrame(self.window)
        save_button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        ctk.CTkButton(save_button_frame, text="Save Settings", command=self.save_settings).pack()

        
    def select_save_location(self):
        folder_path = easygui.diropenbox(title="Select Folder to Save Graphs To")
        if folder_path:
            self.save_folder = folder_path
            
    
                
    def save_settings(self):
        # Convert all variables to their primitive values
        settings = {
            "metrics": {metric: bool(var.get()) for metric, var in self.metrics.items()},
            "show_charts": {chart: bool(var.get()) for chart, var in self.show_charts.items()},
            "save_charts": bool(self.save_charts.get()),
            "chart_groups": self.chart_groups,
            "frame_counts": {metric: str(var.get()) for metric, var in self.metric_frame_counts.items()},
            "save_folder": str(self.save_folder.get()) if isinstance(self.save_folder, tk.StringVar) else str(self.save_folder)
        }

        try:
            with open(self.graph_settings_file, 'w') as f:
                json.dump(settings, f, indent=4)

            if self.callback:
                self.callback()

            print("Graph Settings Saved:", settings)
            self.on_closing()
        except Exception as e:
            print(f"Error saving settings: {e}")


    def on_closing(self):
        """Properly cleanup widgets and destroy window"""
        try:
            if self.window.winfo_exists():
                self.window.grab_release()
                self.window.destroy()
        except tk.TclError as e:
            print(f"Warning during closing: {e}")