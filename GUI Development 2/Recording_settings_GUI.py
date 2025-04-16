import tkinter as tk
from tkinter import ttk
import json
import os
import customtkinter as ctk
import easygui

class RecordingsettingsGUI:
    def __init__(self, root, callback=None):
        self.root = root
        self.callback = callback
        self.settings_file = "recording_settings.json"
        
        #create settings window
        self.window = ctk.CTkToplevel(root)
        self.window.title("Recording Settings")
        
        # Initialize settings with saved values or defaults
        self.init_settings()
        self.load_settings()
        
        #setup window closing protocol
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        #prevent interaction with the main GUI window while open
        self.window.grab_set()
        
        # Add title to Recording Settings window
        title = ctk.CTkLabel(self.window, text="Recording Settings", 
                            font=("Arial", 20, "bold"))
        title.pack(pady=20)
        
        #Setup frames for menu GUI
        self.setup_frames()
        
    def init_settings(self):
        """Initialize settings variables"""
        # Video recording settings
        self.video_raw = ctk.BooleanVar(value=False)
        self.video_annotated = ctk.BooleanVar(value=False)
        self.video_segmented = ctk.BooleanVar(value=False)
        
        # Image recording settings
        self.image_raw = ctk.BooleanVar(value=False)
        self.image_annotated = ctk.BooleanVar(value=False)
        self.image_segmented = ctk.BooleanVar(value=False)
        
        # Exposure time settings
        self.et_mode = ctk.StringVar(value="Fixed")
        self.et_fixed = ctk.StringVar(value="1000")
        self.et_time = ctk.StringVar(value="5")
        self.et_start = ctk.StringVar(value="1000")
        self.et_end = ctk.StringVar(value="10000")
        self.et_step = ctk.StringVar(value="1000")
        
        # RSI mode setting
        self.rsi_mode = ctk.StringVar(value="Manual")
        
        # Initialize recording save location
        self.recording_save_location = ctk.StringVar(value="")

    def load_settings(self):
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    
                    # Load video settings
                    self.video_raw.set(settings.get('video_raw', False))
                    self.video_annotated.set(settings.get('video_annotated', False))
                    self.video_segmented.set(settings.get('video_segmented', False))
                    
                    # Load image settings
                    self.image_raw.set(settings.get('image_raw', False))
                    self.image_annotated.set(settings.get('image_annotated', False))
                    self.image_segmented.set(settings.get('image_segmented', False))
                    
                    # Load exposure settings
                    self.et_mode.set(settings.get('et_mode', 'Fixed'))
                    self.et_fixed.set(settings.get('et_fixed', '1000'))
                    self.et_time.set(settings.get('et_time','5'))
                    self.et_start.set(settings.get('et_start', '1000'))
                    self.et_end.set(settings.get('et_end', '10000'))
                    self.et_step.set(settings.get('et_step', '1000'))
                    
                    # Load save location
                    self.recording_save_location.set(settings.get('recording_save_location', False))
                    
                    # Load RSI mode
                    self.rsi_mode.set(settings.get('rsi_mode', 'Manual'))
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        """Save settings to JSON file"""
        settings = {
            # Video settings
            'video_raw': self.video_raw.get(),
            'video_annotated': self.video_annotated.get(),
            'video_segmented': self.video_segmented.get(),
            
            # Image settings
            'image_raw': self.image_raw.get(),
            'image_annotated': self.image_annotated.get(),
            'image_segmented': self.image_segmented.get(),
            
            # Exposure settings
            'et_mode': self.et_mode.get(),
            'et_fixed': self.et_fixed.get(),
            'et_time':self.et_time.get(),
            'et_start': self.et_start.get(),
            'et_end': self.et_end.get(),
            'et_step': self.et_step.get(),
            
            # RSI mode
            'rsi_mode': self.rsi_mode.get(),
            
            # Save Location
            'recording_save_location': self.recording_save_location.get()
        }
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            if self.callback:
                self.callback()  # Call the update callback
            self.window.destroy()
        except Exception as e:
            print(f"Error saving settings: {e}")

    # Initialize frames within window
    def setup_frames(self):
        # Record Videos section
        Record_videos_frame = ctk.CTkFrame(master=self.window)
        Record_videos_label = ctk.CTkLabel(Record_videos_frame, text="Record Videos", font=("Arial", 16, "bold"))
        Record_videos_label.pack(pady=10, padx=10, anchor="w")
        
        # Create checkboxes using pack
        video_vars = [(self.video_raw, "Raw Video"),
                     (self.video_annotated, "Annotated Video"),
                     (self.video_segmented, "Segmented Video")]
        for var, text in video_vars:
            checkbox = ctk.CTkCheckBox(Record_videos_frame, text=text, variable=var, command=self.handle_image_settings)
            checkbox.pack(pady=5, padx=20, anchor="w")
        
        Record_videos_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Record Images section
        Record_images_frame = ctk.CTkFrame(master=self.window)  
        Record_images_label = ctk.CTkLabel(Record_images_frame, text="Record Images", font=("Arial", 16, "bold"))
        Record_images_label.pack(pady=10, padx=10, anchor="w")  # Add this line to display the label
        
        #Create checkboxes using pack
        images_vars = [(self.image_raw, "Raw Image"),
                        (self.image_annotated, "Annotated Image"),
                        (self.image_segmented, "Segmented Image")]
        for var, text in images_vars:
            checkbox = ctk.CTkCheckBox(Record_images_frame, text=text, variable=var,command=self.handle_video_settings)
            checkbox.pack(pady=5, padx=20, anchor="w")
        Record_images_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        
        # Exposure Time Settings section
        Exposure_time_settings_frame = ctk.CTkFrame(master=self.window)
        Exposure_time_settings_label = ctk.CTkLabel(Exposure_time_settings_frame, 
                                                  text="Exposure Time Settings", 
                                                  font=("Arial", 16, "bold"))
        Exposure_time_settings_label.pack(pady=10, padx=10, anchor="w")

        # Mode selection frame
        et_mode_frame = ctk.CTkFrame(Exposure_time_settings_frame)
        et_mode_frame.pack(fill="x", padx=10, pady=5)

        fixed_radio = ctk.CTkRadioButton(
            et_mode_frame, 
            text="Fixed ET",
            variable=self.et_mode,
            value="Fixed",
            command=self.update_et_fields
        )
        fixed_radio.pack(side="left", padx=20)

        iterate_radio = ctk.CTkRadioButton(
            et_mode_frame,
            text="Iterate ET",
            variable=self.et_mode,
            value="Iterate",
            command=self.update_et_fields
        )
        iterate_radio.pack(side="left", padx=20)

        # Fixed ET frame
        self.fixed_frame = ctk.CTkFrame(Exposure_time_settings_frame)
        fixed_label = ctk.CTkLabel(self.fixed_frame, text="Fixed Exposure Time (μs):")
        fixed_label.pack(side="left", padx=5)
        fixed_entry = ctk.CTkEntry(self.fixed_frame, textvariable=self.et_fixed)
        fixed_entry.pack(side="left", padx=5)

        # Iteration ET frame
        self.iter_frame = ctk.CTkFrame(Exposure_time_settings_frame)
        for label, var in [("Start (μs):", self.et_start),
                         ("End (μs):", self.et_end),
                         ("Step (μs):", self.et_step),
                         ("Iteration Time (s):", self.et_time)]:
            frame = ctk.CTkFrame(self.iter_frame)
            frame.pack(fill="x", pady=2)
            ctk.CTkLabel(frame, text=label).pack(side="left", padx=5)
            ctk.CTkEntry(frame, textvariable=var).pack(side="left", padx=5)

        # Show initial frame based on mode
        if self.et_mode.get() == "Fixed":
            self.fixed_frame.pack(fill="x", padx=20, pady=5)
        else:
            self.iter_frame.pack(fill="x", padx=20, pady=5)

        Exposure_time_settings_frame.pack(pady=10, padx=10, fill="both", expand=True)

        #RSI Integration section
        RSI_integration_frame = ctk.CTkFrame(master=self.window)
        RSI_integration_label = ctk.CTkLabel(RSI_integration_frame, text="RSI Integration", font=("Arial", 16, "bold"))
        RSI_integration_label.pack(pady=10, padx=10, anchor="w")
        
        # Update radio buttons to use pack
        ctk.CTkRadioButton(
            RSI_integration_frame, 
            text="Start recordings manually",
            variable=self.rsi_mode, 
            value="Manual"
        ).pack(pady=5, padx=20, anchor="w")
        
        ctk.CTkRadioButton(
            RSI_integration_frame, 
            text="Start recordings automatically",
            variable=self.rsi_mode, 
            value="Automatic"
        ).pack(pady=5, padx=20, anchor="w")
        
        RSI_integration_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Select Folder Save Button
        save_location_frame = ctk.CTkFrame(master=self.window)
        save_location_label = ctk.CTkLabel(save_location_frame, text="Save Location", padx=5, pady=5)
        save_location_label.pack()
        save_location_frame.pack(fill="x",pady=5,padx=5)
        
        ctk.CTkButton(save_location_frame, text="Select Save Location", command=self.get_recording_save_location).pack(pady=10)
        
        # Save Settings button - changed from grid to pack
        save_button = ctk.CTkButton(
            master=self.window, 
            text="Save Settings",
            command=self.save_settings,  # Added proper method reference
            font=("Arial", 12, "bold")
        )
        save_button.pack(pady=10, padx=10, fill="x")

    def get_recording_save_location(self):
        folder_path = easygui.diropenbox(title="Select Folder to Save Recordings To")
        if folder_path:
            self.recording_save_location.set(folder_path)
    
    # Setup closing function
    def on_closing(self):
        self.window.grab_release()  # Release the grab
        self.window.destroy()  # Close the window
        
    def handle_video_settings(self):
        # Handle video settings here
        if any([self.video_raw.get(), self.video_annotated.get(), self.video_segmented.get()]):
            self.video_raw.set(False)
            self.video_annotated.set(False)
            self.video_segmented.set(False)
            
    def handle_image_settings(self):
        if any([self.image_raw.get(), self.image_annotated.get(), self.image_segmented.get()]):
            self.image_raw.set(False)
            self.image_annotated.set(False)
            self.image_segmented.set(False)
            
    def update_et_fields(self):
        """Show/hide ET fields based on selected mode"""
        if self.et_mode.get() == "Fixed":
            self.iter_frame.pack_forget()
            self.fixed_frame.pack(fill="x", padx=20, pady=5)
        else:
            self.fixed_frame.pack_forget()
            self.iter_frame.pack(fill="x", padx=20, pady=5)

