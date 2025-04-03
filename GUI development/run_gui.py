import tkinter as tk
from gui import MainGUI

def main():
    """
    Run the Welding Monitoring System GUI
    Press Escape to exit fullscreen mode and close the application
    """
    root = tk.Tk()
    app = MainGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
