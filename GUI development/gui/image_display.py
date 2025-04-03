import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import os

class ImageDisplayFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.image_labels = {}
        self.current_layout = None
        self.settings_file = "recording_settings.json"
        
        # Define placeholder sizes to match camera resolution
        self.placeholder_width = 80
        self.placeholder_height = 60
        
        self.setup_display()
        
        # Bind resize event
        self.bind("<Configure>", self.on_resize)
        
        # Grid configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def setup_display(self):
        self.load_settings()
        
        # Store current images if they exist
        current_images = {}
        for img_type, label in self.image_labels.items():
            if hasattr(label, 'image'):
                current_images[img_type] = label.image
        
        # Recreate display
        self.create_image_labels()
        
        # Restore images if they match new layout
        for img_type, image in current_images.items():
            if img_type in self.image_labels:
                self.image_labels[img_type].configure(image=image)
                self.image_labels[img_type].image = image
        
    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = {"video_recording": "None", "image_recording": "None"}
            
    def on_resize(self, event=None):
        """Handle window resize events"""
        if hasattr(self, 'after_id'):
            self.after_cancel(self.after_id)
        self.after_id = self.after(100, self.setup_display)  # Debounce resize events

    def create_image_labels(self):
        # Clear existing labels
        for widget in self.winfo_children():
            widget.destroy()
        self.image_labels = {}

        # Get recording settings
        video_option = self.settings.get("video_recording", "None")
        image_option = self.settings.get("image_recording", "None")
        
        # Don't show anything if no recording options are selected
        if video_option == "None" and image_option == "None":
            return
            
        # Show both frames
        if video_option == "Both" or image_option == "Both":
            container = ttk.Frame(self)
            container.grid(sticky="nsew")
            container.grid_columnconfigure(0, weight=1)
            container.grid_columnconfigure(1, weight=1)
            
            left_frame = ttk.LabelFrame(container, text="Raw Image")
            left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            
            right_frame = ttk.LabelFrame(container, text="Annotated Image")
            right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
            
            # Set initial size for labels
            self.image_labels["raw"] = tk.Label(left_frame, background='black',
                width=self.placeholder_width//2, height=self.placeholder_height//2)
            self.image_labels["raw"].pack(expand=True, fill="both")
            
            self.image_labels["annotated"] = tk.Label(right_frame, background='black',
                width=self.placeholder_width//2, height=self.placeholder_height//2)
            self.image_labels["annotated"].pack(expand=True, fill="both")
            return
            
        # Show single frame for raw or annotated
        if "Raw" in video_option or "Raw" in image_option:
            label_type = "raw"
            frame_title = "Raw Image"
        else:
            label_type = "annotated"
            frame_title = "Annotated Image"
        
        container = ttk.Frame(self)
        container.grid(sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
        main_frame = ttk.LabelFrame(container, text=frame_title)
        main_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.image_labels[label_type] = tk.Label(main_frame, background='black',
            width=self.placeholder_width, height=self.placeholder_height)
        self.image_labels[label_type].pack(expand=True, fill="both")
            
    def update_image(self, image_type, image):
        """Update the display with new image(s)"""
        if image_type in self.image_labels:
            # Convert numpy array to PhotoImage and update label
            photo = ImageTk.PhotoImage(image=Image.fromarray(image))
            self.image_labels[image_type].configure(image=photo)
            self.image_labels[image_type].image = photo  # Keep reference