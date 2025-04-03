def update_gui(display_frame):
    """Update the GUI display without closing the window"""
    if display_frame:
        display_frame.load_settings()  # Reload settings
        display_frame.update_display([])  # Clear current display
        display_frame.update_idletasks()  # Force GUI update
