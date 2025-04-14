import customtkinter as ctk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Color map for features
FEATURE_COLORS = {
    "Solidification Zone": "#1f77b4",
    "Welding Wire": "#ff7f0e",
    "Arc Flash": "#2ca02c"
}

# Function to plot on a given axis
def plot_feature_on_axes(ax, feature_name, x_data, y_data, desired_value, tol_pos, tol_neg, title, xlabel, ylabel):
    
    FEATURE_COLORS = {
    "Solidification Zone": "#1f77b4",
    "Welding Wire": "#ff7f0e",
    "Arc Flash": "#2ca02c"
    }
    
    color = FEATURE_COLORS.get(feature_name, "black")

    ax.plot(x_data, y_data, label=feature_name, color=color)
    ax.axhline(desired_value, color=color, linestyle='--', linewidth=1)
    ax.fill_between(x_data, desired_value - tol_neg, desired_value + tol_pos, color=color, alpha=0.2)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()

# Setup main CTk window
root = ctk.CTk()
root.geometry("1000x800")
root.title("2x2 Feature Plot Viewer")

# Frame to hold the chart
chart_frame = ctk.CTkFrame(root)
chart_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Sample data for each graph
x = list(range(100))
data_sets = [
    ("Solidification Zone", np.random.normal(150, 5, size=100), 150, 10, 5),
    ("Welding Wire", np.random.normal(200, 3, size=100), 200, 6, 4),
    ("Arc Flash", np.random.normal(180, 8, size=100), 180, 12, 8),
    ("Solidification Zone", np.random.normal(145, 7, size=100), 150, 10, 5),  # Second instance, could be different metric
]

# Create a 2x2 grid of plots on a single figure
fig = Figure(figsize=(10, 8), dpi=100)
axes = [fig.add_subplot(2, 2, i+1) for i in range(4)]

# Plot each dataset into the appropriate subplot
for ax, (feature, y_data, desired, tol_pos, tol_neg) in zip(axes, data_sets):
    plot_feature_on_axes(
        ax,
        feature_name=feature,
        x_data=x,
        y_data=y_data,
        desired_value=desired,
        tol_pos=tol_pos,
        tol_neg=tol_neg,
        title=f"{feature} Tracking",
        xlabel="Frame Index",
        ylabel="Pixel Position"
    )

# Embed the figure into the CTk frame
canvas = FigureCanvasTkAgg(fig, master=chart_frame)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True)

# Run the GUI loop
root.mainloop()
