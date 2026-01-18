import customtkinter as ctk
from typing import Optional, Callable
import time

class MetricCard(ctk.CTkFrame):
    """
    A dashboard card displaying a single metric (e.g., CPU Usage).
    """
    def __init__(self, master, title: str, unit: str = "%", color: str = "#1f6aa5", **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title
        self.lbl_title = ctk.CTkLabel(self, text=title, font=("Roboto Medium", 14), text_color="gray70")
        self.lbl_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        # Value
        self.lbl_value = ctk.CTkLabel(self, text=f"0{unit}", font=("Roboto", 32, "bold"), text_color="white")
        self.lbl_value.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # Progress Bar
        self.progress = ctk.CTkProgressBar(self, height=8, progress_color=color)
        self.progress.grid(row=2, column=0, padx=10, pady=(0, 15), sticky="ew")
        self.progress.set(0)
        
        self.unit = unit

    def update_metric(self, value: float, display_str: Optional[str] = None):
        """
        Update the card. 
        value: 0.0 to 100.0 (or normalized 0.0-1.0 if strict)
        """
        # Update text
        if display_str:
            self.lbl_value.configure(text=display_str)
        else:
            self.lbl_value.configure(text=f"{value:.1f}{self.unit}")
        
        # Update progress bar (expecting 0-100 input, converting to 0.0-1.0)
        # Clamp between 0 and 1
        norm_val = max(0.0, min(1.0, value / 100.0))
        self.progress.set(norm_val)

class ConsoleWidget(ctk.CTkTextbox):
    """
    A read-only console output widget with timestamping.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, font=("Consolas", 12), activate_scrollbars=True, **kwargs)
        self.configure(state="disabled")
        self.tag_config("info", foreground="cyan")
        self.tag_config("error", foreground="red")
        self.tag_config("success", foreground="#2cc985")
        self.tag_config("warning", foreground="orange")
        
    def log(self, message: str, level: str = "info"):
        self.configure(state="normal")
        timestamp = time.strftime("[%H:%M:%S]")
        
        # Insert timestamp
        self.insert("end", f"{timestamp} ", "timestamp")
        
        # Insert message with color tag
        self.insert("end", f"{message}\n", level)
        
        self.see("end")
        self.configure(state="disabled")

class ActionButton(ctk.CTkButton):
    """
    Standardized action button.
    """
    def __init__(self, master, text: str, command: Callable, type: str = "primary", **kwargs):
        colors = {
            "primary": "#1f6aa5",
            "danger": "#c0392b",
            "success": "#27ae60",
            "warning": "#d35400"
        }
        hover_colors = {
            "primary": "#144870",
            "danger": "#922b21",
            "success": "#1e8449",
            "warning": "#a04000"
        }
        
        super().__init__(
            master, 
            text=text, 
            command=command, 
            fg_color=colors.get(type, colors["primary"]),
            hover_color=hover_colors.get(type, hover_colors["primary"]),
            height=36,
            font=("Roboto Medium", 13),
            **kwargs
        )
