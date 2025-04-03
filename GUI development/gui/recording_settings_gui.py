import tkinter as tk
from tkinter import ttk
import json
import os
from .update_gui import update_gui

class RecordingSettingsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Recording Settings")
        self.settings_file = "recording_settings.json"
        
        # Initialize video recording settings
        self.video_raw = tk.BooleanVar(value=False)
        self.video_annotated = tk.BooleanVar(value=False)
        self.video_segmented = tk.BooleanVar(value=False)
        
        # Initialize image recording settings
        self.image_raw = tk.BooleanVar(value=False)
        self.image_annotated = tk.BooleanVar(value=False)
        self.image_segmented = tk.BooleanVar(value=False)
        
        # Initialize exposure time settings
        self.et_mode = tk.StringVar(value="Fixed")  # "Fixed" or "Iterate"
        self.et_fixed = tk.StringVar(value="1000")  # Fixed exposure time in microseconds
        self.et_start = tk.StringVar(value="1000")  # Start of iteration range
        self.et_end = tk.StringVar(value="10000")   # End of iteration range
        self.et_step = tk.StringVar(value="1000")   # Step size for iteration
        
        # Add RSI mode setting
        self.rsi_mode = tk.StringVar(value="Manual")  # "Manual" or "RSI"
        
        self.load_settings()
        self.create_widgets()
    
    def load_settings(self):
        """Load existing settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    
                    # Handle video settings
                    video_settings = settings.get("video_recording", {})
                    if isinstance(video_settings, dict):
                        self.video_raw.set(video_settings.get("raw", False))
                        self.video_annotated.set(video_settings.get("annotated", False))
                        self.video_segmented.set(video_settings.get("segmented", False))
                    else:
                        # Handle legacy format or invalid data
                        self.video_raw.set(False)
                        self.video_annotated.set(False)
                        self.video_segmented.set(False)
                    
                    # Handle image settings
                    image_settings = settings.get("image_recording", {})
                    if isinstance(image_settings, dict):
                        self.image_raw.set(image_settings.get("raw", False))
                        self.image_annotated.set(image_settings.get("annotated", False))
                        self.image_segmented.set(image_settings.get("segmented", False))
                    else:
                        # Handle legacy format or invalid data
                        self.image_raw.set(False)
                        self.image_annotated.set(False)
                        self.image_segmented.set(False)
                    
                    # Load exposure time settings
                    et_settings = settings.get("exposure_time", {})
                    if isinstance(et_settings, dict):
                        self.et_mode.set(et_settings.get("mode", "Fixed"))
                        self.et_fixed.set(et_settings.get("fixed_value", "1000"))
                        self.et_start.set(et_settings.get("start", "1000"))
                        self.et_end.set(et_settings.get("end", "10000"))
                        self.et_step.set(et_settings.get("step", "1000"))
                    
                    # Load RSI mode
                    self.rsi_mode.set(settings.get("rsi_mode", "Manual"))
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"Error loading settings: {e}")
            # Use default values if settings file is corrupted
    
    def handle_video_selection(self, *args):
        """When any video option is selected, disable all image options"""
        if any([self.video_raw.get(), self.video_annotated.get(), self.video_segmented.get()]):
            self.image_raw.set(False)
            self.image_annotated.set(False)
            self.image_segmented.set(False)
    
    def handle_image_selection(self, *args):
        """When any image option is selected, disable all video options"""
        if any([self.image_raw.get(), self.image_annotated.get(), self.image_segmented.get()]):
            self.video_raw.set(False)
            self.video_annotated.set(False)
            self.video_segmented.set(False)

    def validate_exposure_time(self, value):
        """Validate exposure time inputs"""
        try:
            val = int(value)
            return val >= 0 and val <= 1000000  # Maximum 1 second
        except ValueError:
            return False
        
    def create_widgets(self):
        # Configure grid weight
        self.root.grid_columnconfigure(0, weight=1)
        
        # Title for the window
        title_label = tk.Label(self.root, text="Recording Settings", font=("Arial", 14))
        title_label.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

        # Record Videos Section
        video_frame = ttk.LabelFrame(self.root, text="Record Videos", padding="10")
        video_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        video_frame.grid_columnconfigure(0, weight=1)

        video_vars = [(self.video_raw, "Raw Video"),
                     (self.video_annotated, "Annotated Video"),
                     (self.video_segmented, "Segmented Video")]
        
        for idx, (var, text) in enumerate(video_vars):
            tk.Checkbutton(video_frame, text=text, variable=var,
                          command=self.handle_video_selection).grid(
                              row=idx, column=0, padx=5, pady=2, sticky="w")
        
        # Record Images Section
        image_frame = ttk.LabelFrame(self.root, text="Record Images", padding="10")
        image_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        image_frame.grid_columnconfigure(0, weight=1)

        image_vars = [(self.image_raw, "Raw Image"),
                     (self.image_annotated, "Annotated Image"),
                     (self.image_segmented, "Segmented Image")]
        
        for idx, (var, text) in enumerate(image_vars):
            tk.Checkbutton(image_frame, text=text, variable=var,
                          command=self.handle_image_selection).grid(
                              row=idx, column=0, padx=5, pady=2, sticky="w")

        # Exposure Time Section
        et_frame = ttk.LabelFrame(self.root, text="Exposure Time Settings", padding="10")
        et_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        et_frame.grid_columnconfigure(0, weight=1)

        # Mode selection
        mode_frame = ttk.Frame(et_frame)
        mode_frame.grid(row=0, column=0, pady=5, sticky="ew")
        mode_frame.grid_columnconfigure(0, weight=1)

        ttk.Radiobutton(mode_frame, text="Fixed ET", variable=self.et_mode, 
                       value="Fixed", command=self.update_et_fields).grid(row=0, column=0, padx=5, sticky="w")
        ttk.Radiobutton(mode_frame, text="Iterate ET", variable=self.et_mode, 
                       value="Iterate", command=self.update_et_fields).grid(row=0, column=1, padx=5, sticky="w")

        # Fixed ET settings
        self.fixed_frame = ttk.Frame(et_frame)
        self.fixed_frame.grid(row=1, column=0, pady=5, sticky="ew")
        
        ttk.Label(self.fixed_frame, text="Fixed ET (μs):").grid(row=0, column=0, padx=5)
        vcmd = (self.root.register(self.validate_exposure_time), '%P')
        ttk.Entry(self.fixed_frame, textvariable=self.et_fixed, width=10,
                 validate='key', validatecommand=vcmd).grid(row=0, column=1, padx=5)

        # Iteration settings
        self.iter_frame = ttk.Frame(et_frame)
        self.iter_frame.grid(row=1, column=0, pady=5, sticky="ew")
        
        labels = ["Start (μs):", "End (μs):", "Step (μs):"]
        vars = [self.et_start, self.et_end, self.et_step]
        
        for i, (label, var) in enumerate(zip(labels, vars)):
            ttk.Label(self.iter_frame, text=label).grid(row=i, column=0, padx=5, pady=2)
            ttk.Entry(self.iter_frame, textvariable=var, width=10,
                     validate='key', validatecommand=vcmd).grid(row=i, column=1, padx=5, pady=2)

        # RSI Integration Section
        rsi_frame = ttk.LabelFrame(self.root, text="RSI Integration", padding="10")
        rsi_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        rsi_frame.grid_columnconfigure(0, weight=1)

        ttk.Radiobutton(rsi_frame, text="Start recordings manually", 
                       variable=self.rsi_mode, value="Manual").grid(row=0, column=0, pady=2, sticky="w")
        ttk.Radiobutton(rsi_frame, text="Listen for RSI Signal", 
                       variable=self.rsi_mode, value="RSI").grid(row=1, column=0, pady=2, sticky="w")
        
        # Save Button
        save_button = tk.Button(self.root, text="Save Settings", command=self.save_settings)
        save_button.grid(row=5, column=0, pady=10)

        # Call update_et_fields to show/hide appropriate frames
        self.update_et_fields()

    def update_et_fields(self):
        """Show/hide ET fields based on selected mode"""
        if self.et_mode.get() == "Fixed":
            self.iter_frame.grid_remove()
            self.fixed_frame.grid()
        else:
            self.fixed_frame.grid_remove()
            self.iter_frame.grid()

    def get_active_selections(self):
        """Get list of active recording selections"""
        active = []
        if self.video_raw.get():
            active.append("Raw Video")
        if self.video_annotated.get():
            active.append("Annotated Video")
        if self.video_segmented.get():
            active.append("Segmented Video")
        if self.image_raw.get():
            active.append("Raw Image")
        if self.image_annotated.get():
            active.append("Annotated Image")
        if self.image_segmented.get():
            active.append("Segmented Image")
        return active

    def save_settings(self):
        settings = {
            "video_recording": {
                "raw": self.video_raw.get(),
                "annotated": self.video_annotated.get(),
                "segmented": self.video_segmented.get()
            },
            "image_recording": {
                "raw": self.image_raw.get(),
                "annotated": self.image_annotated.get(),
                "segmented": self.image_segmented.get()
            },
            "exposure_time": {
                "mode": self.et_mode.get(),
                "fixed_value": self.et_fixed.get(),
                "start": self.et_start.get(),
                "end": self.et_end.get(),
                "step": self.et_step.get()
            },
            "rsi_mode": self.rsi_mode.get()
        }
        
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        
        # Get only image selections
        active_images = [s for s in self.get_active_selections() if "Image" in s]
        
        # Update GUI using the new update function
        if hasattr(self.root, 'master') and hasattr(self.root.master, 'display_frame'):
            display_frame = self.root.master.display_frame
            update_gui(display_frame)
            display_frame.update_display(active_images)
        
        print("Recording Settings Saved:", settings)
        self.root.destroy()