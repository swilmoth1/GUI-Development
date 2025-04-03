import tkinter as tk
from tkinter import ttk
import json
import os
from .annotation_settings_gui import AnnotationSettingsGUI
from .recording_settings_gui import RecordingSettingsGUI
from .segmentation_settings_gui import SegmentationAndClassGUI
from .graph_settings_gui import GraphSettingsGUI
from .material_defaults_gui import MaterialDefaultsGUI
from .update_gui import update_gui
from .image_display import ImageDisplayFrame

class DisplayFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.image_labels = []  # Store references to image labels
        self.setup_display()
        self.load_settings()  # Load initial settings
        
    def setup_display(self):
        """Initial setup of the display area"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # Create initial default display
        label = ttk.Label(self, text="No image display selected")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.image_labels.append(label)
        
    
        

    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists("recording_settings.json"):
                with open("recording_settings.json", 'r') as f:
                    settings = json.load(f)
                    # Update display based on loaded settings
                    image_settings = settings.get("image_recording", {})
                    active = []
                    if image_settings.get("raw", False):
                        active.append("Raw Image")
                    if image_settings.get("annotated", False):
                        active.append("Annotated Image")
                    if image_settings.get("segmented", False):
                        active.append("Segmented Image")
                    self.update_display(active)
        except Exception as e:
            print(f"Error loading settings: {e}")

    def refresh(self):
        """Refresh the display frame"""
        update_gui(self)

class MainGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WAAM Deposition Monitoring System")
        
        # Set window to fullscreen
        self.root.state('zoomed')  # For Windows
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Enable fullscreen toggle with F11 and exit with Escape
        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.quit_fullscreen)
        
        # Add status message variable
        self.status_message = tk.StringVar(value="Ready to record...")
        
        # Add recording state
        self.is_recording = False
        
        # Add alert state
        self.alert_message = tk.StringVar(value="")
        
        # Add window tracking
        self.open_windows = {
            'recording': None,
            'segmentation': None,
            'annotation': None,
            'graph': None,
            'material': None
        }
        
        # Configure grid
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.grid(row=0, column=0, sticky="nsew")
        
        # Add alert frame at the top
        alert_frame = ttk.Frame(main_container)
        alert_frame.grid(row=0, column=0, sticky="ew", padx=5)
        self.alert_label = ttk.Label(alert_frame, textvariable=self.alert_message,
                                   foreground='red', font=("Arial", 12, "bold"))
        self.alert_label.pack(pady=5)
        
        # Adjust row configurations
        main_container.grid_rowconfigure(0, weight=0)  # Alert frame
        main_container.grid_rowconfigure(1, weight=0)  # Control panel
        main_container.grid_rowconfigure(2, weight=1)  # Image display
        main_container.grid_rowconfigure(3, weight=1)  # Graphical display bar
        main_container.grid_rowconfigure(4, weight=0)  # Status bar
        
        
        # Control panel frame in row 1
        control_frame = ttk.LabelFrame(main_container, text="Control Panel")
        control_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        # Left side buttons
        left_button_frame = ttk.Frame(control_frame)
        left_button_frame.pack(side="left", fill="y")
        
        buttons = [
            ("Segmentation Settings", self.open_segmentation_and_class_gui),
            ("Recording Settings", self.open_recording_settings_gui),
            ("Annotation Settings", self.open_annotation_settings_gui),
            ("Graph Settings", self.open_graph_settings_gui),
            ("Material Defaults", self.open_material_defaults_gui)
        ]
        
        for text, command in buttons:
            ttk.Button(left_button_frame, text=text, command=command).pack(side="left", padx=5, pady=5)
        
        # Center the record button
        record_frame = ttk.Frame(control_frame)
        record_frame.pack(side="left", fill="both", expand=True, padx=20)
        
        self.record_button = tk.Button(record_frame, text="Start Recording", 
                                     command=self.toggle_recording,
                                     font=("Arial", 14, "bold"),
                                     bg="green", fg="white",
                                     height=2)
        self.record_button.pack(expand=True)
        
        # Right side exit button
        exit_button = ttk.Button(control_frame, text="Exit", command=self.root.quit)
        exit_button.pack(side="right", padx=5, pady=5)
        
        # Image display now goes in row 2
        self.display_frame = DisplayFrame(main_container)
        self.display_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        
        # Graphical image now goes in row 3
        self.display_graph = DisplayFrame(main_container)
        self.display_graph.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        
        
        # Status bar now goes in row 4
        
        status_frame = ttk.Frame(main_container)
        status_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=2)
        status_label = ttk.Label(status_frame, textvariable=self.status_message)
        status_label.pack(side="left", padx=5)
    
    def toggle_recording(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.record_button.config(text="Stop Recording", bg="red")
            self.status_message.set("Recording in progress...")
        else:
            self.record_button.config(text="Start Recording", bg="green")
            self.status_message.set("Recording stopped.")
    
    def handle_window_close(self, window_type):
        """Handle cleanup when a settings window is closed"""
        if window_type in self.open_windows:
            window = self.open_windows[window_type]
            if window and window.winfo_exists():
                window.destroy()
            self.open_windows[window_type] = None
    
    def open_recording_settings_gui(self):
        if self.open_windows['recording'] and self.open_windows['recording'].winfo_exists():
            try:
                self.open_windows['recording'].focus_force()
            except:
                self.handle_window_close('recording')
                recording_setting_window = tk.Toplevel(self.root)
                recording_setting_window.focus_force()
                self.open_windows['recording'] = recording_setting_window
                RecordingSettingsGUI(recording_setting_window)
            return
        recording_setting_window = tk.Toplevel(self.root)
        recording_setting_window.focus_force()
        recording_setting_window.protocol("WM_DELETE_WINDOW", 
                                       lambda: self.handle_window_close('recording'))
        self.open_windows['recording'] = recording_setting_window
        RecordingSettingsGUI(recording_setting_window)

    def open_settings_window(self, window_type, gui_class):
        """Generic method to handle opening settings windows"""
        if self.open_windows[window_type] and self.open_windows[window_type].winfo_exists():
            try:
                self.open_windows[window_type].focus_force()
            except:
                self.handle_window_close(window_type)
                window = tk.Toplevel(self.root)
                window.focus_force()
                self.open_windows[window_type] = window
                gui_class(window)
            return
        window = tk.Toplevel(self.root)
        window.focus_force()
        window.protocol("WM_DELETE_WINDOW", 
                       lambda: self.handle_window_close(window_type))
        self.open_windows[window_type] = window
        gui_class(window)

    # Update other window opening methods to use the generic method
    def open_segmentation_and_class_gui(self):
        self.open_settings_window('segmentation', SegmentationAndClassGUI)
        
    def open_annotation_settings_gui(self):
        self.open_settings_window('annotation', AnnotationSettingsGUI)
        
    def open_graph_settings_gui(self):
        self.open_settings_window('graph', GraphSettingsGUI)
        
    def open_material_defaults_gui(self):
        self.open_settings_window('material', MaterialDefaultsGUI)
        
    def show_alert(self, message):
        """Display an alert message at the top of the window"""
        self.alert_message.set(message)
        
    def clear_alert(self):
        """Clear the alert message"""
        self.alert_message.set("")

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        return "break"
    
    def quit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.root.attributes('-fullscreen', False)
        self.root.state('zoomed')  # Keep maximized when exiting fullscreen
        return "break"
