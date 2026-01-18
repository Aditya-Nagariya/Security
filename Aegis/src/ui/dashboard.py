import customtkinter as ctk
import threading
import time
from typing import Dict, Any

from src.core.system_interface import SystemInterface
from src.core.metrics import SystemMetrics
from src.ui.components import MetricCard, ConsoleWidget, ActionButton

class DashboardWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Core Systems
        self.sys_interface = SystemInterface(simulation_mode="auto")
        
        # Window Setup
        self.title(f"Aegis Security Control [{'SIMULATION' if self.sys_interface.simulation_mode else 'ACTIVE'}]")
        self.geometry("1100x700")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Layout Config
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create UI
        self._create_sidebar()
        self._create_main_view()
        
        # Start Threads
        self.running = True
        self.metrics_thread = threading.Thread(target=self._update_metrics_loop, daemon=True)
        self.metrics_thread.start()
        
        # Welcome Message
        self.console.log("System Initialized.", "success")
        if self.sys_interface.simulation_mode:
            self.console.log("Running in SIMULATION mode (Safe for macOS/Windows)", "warning")
        else:
            self.console.log("Running in ACTIVE Linux mode", "danger")

    def _create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        # Logo / Title
        self.lbl_logo = ctk.CTkLabel(self.sidebar, text="AEGIS", font=("Roboto", 24, "bold"))
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation Buttons (Placeholders for now)
        self.btn_dash = ctk.CTkButton(self.sidebar, text="Dashboard", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.btn_dash.grid(row=1, column=0, padx=20, pady=10)
        
        # System Info Badge
        info = SystemMetrics.get_static_info()
        self.lbl_sysinfo = ctk.CTkLabel(
            self.sidebar, 
            text=f"{info['node']}\n{info['system']}",
            font=("Roboto", 10),
            text_color="gray60"
        )
        self.lbl_sysinfo.grid(row=5, column=0, padx=20, pady=20)

    def _create_main_view(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1) # Console expands
        
        # 1. Metrics Row
        self.metrics_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.metrics_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.metrics_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.card_cpu = MetricCard(self.metrics_frame, "CPU Usage", color="#3498db")
        self.card_cpu.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        self.card_ram = MetricCard(self.metrics_frame, "Memory", color="#9b59b6")
        self.card_ram.grid(row=0, column=1, padx=10, sticky="ew")
        
        self.card_disk = MetricCard(self.metrics_frame, "Disk Space", color="#e67e22")
        self.card_disk.grid(row=0, column=2, padx=(10, 0), sticky="ew")
        
        # 2. Console / Actions Split
        self.split_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.split_frame.grid(row=1, column=0, sticky="nsew")
        self.split_frame.grid_columnconfigure(0, weight=3) # Console wider
        self.split_frame.grid_columnconfigure(1, weight=1) # Actions narrower
        self.split_frame.grid_rowconfigure(0, weight=1)
        
        # Console
        self.console_frame = ctk.CTkFrame(self.split_frame)
        self.console_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.console_frame.grid_columnconfigure(0, weight=1)
        self.console_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(self.console_frame, text="System Log", font=("Roboto Medium", 14)).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.console = ConsoleWidget(self.console_frame)
        self.console.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Actions Panel
        self.actions_frame = ctk.CTkFrame(self.split_frame)
        self.actions_frame.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(self.actions_frame, text="Quick Actions", font=("Roboto Medium", 14)).pack(anchor="w", padx=15, pady=15)
        
        ActionButton(self.actions_frame, "🛡️ System Scan", self._action_scan).pack(fill="x", padx=15, pady=5)
        ActionButton(self.actions_frame, "🧹 Clean Temp", self._action_clean, type="warning").pack(fill="x", padx=15, pady=5)
        ActionButton(self.actions_frame, "🔒 Hardening", self._action_harden, type="danger").pack(fill="x", padx=15, pady=5)
        ActionButton(self.actions_frame, "📦 Update All", self._action_update, type="success").pack(fill="x", padx=15, pady=5)

    def _update_metrics_loop(self):
        """Background thread for metrics"""
        while self.running:
            try:
                metrics = SystemMetrics.get_realtime_metrics()
                
                # Update UI from main thread
                self.after(0, self._update_cards, metrics)
                
                time.sleep(1)
            except Exception as e:
                print(f"Metrics Error: {e}")

    def _update_cards(self, metrics):
        self.card_cpu.update_metric(metrics["cpu"]["usage"])
        self.card_ram.update_metric(metrics["memory"]["percent"], metrics["memory"]["used"])
        self.card_disk.update_metric(metrics["disk"]["percent"], metrics["disk"]["free"] + " Free")

    # --- Actions ---
    
    def _run_threaded_action(self, func, name):
        def task():
            self.after(0, lambda: self.console.log(f"Starting {name}...", "info"))
            result = func()
            
            # Show output
            if result.return_code == 0:
                self.after(0, lambda: self.console.log(result.stdout.strip(), "success"))
            else:
                self.after(0, lambda: self.console.log(f"Error: {result.stderr}", "error"))
                
        threading.Thread(target=task, daemon=True).start()

    def _action_scan(self):
        # Example: Run lynis (simulated)
        self._run_threaded_action(
            lambda: self.sys_interface.run_command(["lynis", "audit", "system"], require_sudo=True),
            "Security Audit"
        )

    def _action_clean(self):
        self._run_threaded_action(
            lambda: self.sys_interface.run_command(["rm", "-rf", "/tmp/*"], require_sudo=False),
            "Temp Cleanup"
        )
        
    def _action_harden(self):
        self._run_threaded_action(
            lambda: self.sys_interface.run_command(["ufw", "enable"], require_sudo=True),
            "Firewall Hardening"
        )
        
    def _action_update(self):
        self._run_threaded_action(
            lambda: self.sys_interface.run_command(["apt", "upgrade", "-y"], require_sudo=True),
            "System Update"
        )

    def on_closing(self):
        self.running = False
        self.destroy()

if __name__ == "__main__":
    app = DashboardWindow()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
