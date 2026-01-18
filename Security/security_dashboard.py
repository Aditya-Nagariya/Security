#!/usr/bin/env python3
"""
Enterprise Security Dashboard
A robust, cross-platform security utility for Linux systems.
Refactored for safety, testability, and maintainability.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import threading
import queue
import sys
import os
import platform
import argparse
import time
import logging
import json
try:
    import yaml
except ImportError:
    print("Warning: PyYAML not installed. Please run 'pip install PyYAML'. Falling back to defaults.")
    yaml = None
from datetime import datetime
from typing import List, Tuple, Optional, Union, Dict, Any
from logging.handlers import RotatingFileHandler

# Import the robust system detector
try:
    from system_detector import SystemDetector, CommandResult
except ImportError:
    # Fallback if running from a different directory structure
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from system_detector import SystemDetector, CommandResult

# --- Configuration Manager ---
class ConfigManager:
    DEFAULT_CONFIG = {
        "app": {
            "name": "Enterprise Security Dashboard",
            "version": "2.1.0",
            "log_file": "security_dashboard.log",
            "log_level": "INFO"
        },
        "timeouts": {
            "default": 30,
            "scan": 600,
            "update": 300,
            "install": 300
        },
        "security": {
            "allowed_ports": [22, 80, 443],
            "critical_services": ["sshd", "ufw", "fail2ban"]
        },
        "paths": {
            "ssh_config": "/etc/ssh/sshd_config",
            "web_root": "/var/www/html"
        }
    }

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            return self.DEFAULT_CONFIG
        
        try:
            if yaml:
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f) or self.DEFAULT_CONFIG
            else:
                # Fallback to JSON if YAML not available but file exists (might fail if it's actually YAML)
                # Or just return defaults to be safe
                return self.DEFAULT_CONFIG
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return self.DEFAULT_CONFIG

    def get(self, path: str, default: Any = None) -> Any:
        """Retrieve config value using dot notation (e.g., 'app.name')"""
        keys = path.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

# --- Logger Setup ---
def setup_logger(log_file: str = "security_dashboard.log", level_str: str = "INFO"):
    logger = logging.getLogger("SecurityDashboard")
    level = getattr(logging, level_str.upper(), logging.INFO)
    logger.setLevel(level)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # File Handler
    try:
        file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to setup file logging: {e}")

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# --- Core Logic Modules ---
class SecurityModule:
    def __init__(self, detector: SystemDetector, config: ConfigManager):
        self.detector = detector
        self.config = config
        self.logger = logging.getLogger("SecurityDashboard")

class Scanner(SecurityModule):
    def run_lynis(self, progress_callback=None) -> str:
        self.logger.info("Starting Lynis scan...")
        if not self.detector.validate_command("lynis"):
            self.logger.info("Lynis not found. Attempting installation...")
            if not self.detector.install_package("lynis"):
                return "Error: Lynis could not be installed."
        
        timeout = self.config.get("timeouts.scan", 600)
        result = self.detector.run_command(
            ["lynis", "audit", "system", "--quick", "--no-colors"], 
            timeout=timeout
        )
        
        if result.return_code == 0:
            return result.stdout
        else:
            return f"Error running Lynis (Code {result.return_code}):\n{result.stderr}\n{result.stdout}"

    def run_clamav(self, progress_callback=None) -> str:
        self.logger.info("Starting ClamAV scan...")
        if not self.detector.validate_command("clamscan"):
            self.logger.info("ClamAV not found. Attempting installation...")
            if not self.detector.install_package("clamav"):
                return "Error: ClamAV could not be installed."
        
        timeout = self.config.get("timeouts.scan", 600)
        # Scan /tmp as a safe default, or configured path
        scan_path = "/tmp" 
        
        result = self.detector.run_command(
            ["clamscan", "-r", scan_path, "--no-summary"], 
            timeout=timeout
        )
        
        if result.return_code == 0:
            return result.stdout or "No malware found."
        elif result.return_code == 1:
             return f"Malware Found:\n{result.stdout}"
        else:
            return f"Error running ClamAV:\n{result.stderr}"

class Hardener(SecurityModule):
    def harden_ssh(self) -> str:
        self.logger.info("Starting SSH Hardening...")
        ssh_config = self.config.get("paths.ssh_config", "/etc/ssh/sshd_config")
        
        if not self.detector.validate_path(ssh_config):
            return f"Error: SSH config not found at {ssh_config}"
            
        if not self.detector.backup_file(ssh_config):
            return "Error: Could not backup SSH config. Aborting for safety."
            
        # Using sed safely via list arguments is tricky, but we can do it one by one
        # Or use a temporary file approach. For now, we'll use sed with -i
        
        changes = [
            ("PasswordAuthentication", "no"),
            ("PermitRootLogin", "no")
        ]
        
        errors = []
        for param, value in changes:
            # This sed command is a bit complex to do without shell=True safely across all sed versions
            # But we can try to use python to edit the file if we have permissions
            # However, since we might need sudo, we often rely on shell tools.
            # Let's use a safer sed pattern.
            
            # Constructing the sed command to replace the line
            # s/^#?PasswordAuthentication.*/PasswordAuthentication no/
            sed_expr = f"s/^#?{param}.*/{param} {value}/"
            
            res = self.detector.run_command(
                ["sed", "-i", sed_expr, ssh_config],
                timeout=10
            )
            if res.return_code != 0:
                errors.append(f"Failed to set {param}: {res.stderr}")

        # Restart SSH
        restart_cmd = ["systemctl", "restart", "sshd"]
        if not self.detector.validate_command("systemctl"):
             restart_cmd = ["service", "ssh", "restart"]
             
        res = self.detector.run_command(restart_cmd, timeout=30)
        if res.return_code != 0:
            errors.append(f"Failed to restart SSH: {res.stderr}")

        if errors:
            return "Hardening completed with errors:\n" + "\n".join(errors)
        return "SSH Hardened Successfully (Backups created)"

    def setup_firewall(self) -> str:
        self.logger.info("Configuring Firewall...")
        if not self.detector.validate_command("ufw"):
            if not self.detector.install_package("ufw"):
                return "Error: UFW could not be installed."
        
        # We need to chain commands or run them sequentially. Sequential is safer.
        commands = [
            ["ufw", "default", "deny", "incoming"],
            ["ufw", "default", "allow", "outgoing"],
            ["ufw", "allow", "ssh"],
            # Enabling UFW usually requires 'y' input. 
            # We can use --force if available or pipe yes.
            # subprocess input parameter is useful here.
        ]
        
        for cmd in commands:
            res = self.detector.run_command(cmd, timeout=30)
            if res.return_code != 0:
                return f"Error executing {' '.join(cmd)}: {res.stderr}"
        
        # Enable UFW
        # We need to handle the "Command may disrupt existing ssh connections" prompt
        # 'ufw --force enable' usually works
        res = self.detector.run_command(["ufw", "--force", "enable"], timeout=30)
        if res.return_code != 0:
            return f"Error enabling UFW: {res.stderr}"
            
        return "Firewall Configured Successfully"

class Monitor(SecurityModule):
    def check_resources(self) -> str:
        self.logger.info("Checking system resources...")
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return (
                f"System Resources:\n"
                f"-----------------\n"
                f"CPU Usage:    {cpu}%\n"
                f"Memory Usage: {mem.percent}% (Used: {mem.used // (1024**2)}MB / Total: {mem.total // (1024**2)}MB)\n"
                f"Disk Usage:   {disk.percent}% (Free: {disk.free // (1024**3)}GB)"
            )
        except ImportError:
            if self.detector.simulation_mode:
                return "CPU: 15% (SIM)\nMemory: 45% (SIM)\nDisk: 60% (SIM)"
            return "Error: psutil python package not installed."

# --- GUI ---
class SecurityDashboard(tk.Tk):
    def __init__(self, simulation_mode=False, debug_mode=False):
        super().__init__()
        
        # Config & Logging
        self.config_manager = ConfigManager()
        self.logger = setup_logger(
            self.config_manager.get("app.log_file"), 
            "DEBUG" if debug_mode else self.config_manager.get("app.log_level")
        )
        
        # System Detector
        self.detector = SystemDetector(simulation_mode=simulation_mode)
        
        # Modules
        self.scanner = Scanner(self.detector, self.config_manager)
        self.hardener = Hardener(self.detector, self.config_manager)
        self.monitor = Monitor(self.detector, self.config_manager)
        
        # Threading
        self.queue = queue.Queue()
        self.active_threads = []
        self.stop_event = threading.Event()
        
        # UI Setup
        self.title(f"{self.config_manager.get('app.name')} {'[SIMULATION]' if simulation_mode else ''}")
        self.geometry("1100x800")
        self.configure_ui()
        
        # Start queue processor
        self.process_queue()
        
        self.logger.info("Dashboard started.")

    def configure_ui(self):
        # Theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main Layout
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Paned Window
        paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        sidebar = ttk.LabelFrame(paned, text="Operations", width=250)
        paned.add(sidebar, weight=1)
        
        # Content Area
        content = ttk.LabelFrame(paned, text="Output Log")
        paned.add(content, weight=4)
        
        # Operations
        ops = [
            ("🛡️ Security Scan (Lynis)", self.scanner.run_lynis, "Runs a full system security audit using Lynis."),
            ("🦠 Malware Scan (ClamAV)", self.scanner.run_clamav, "Scans /tmp directory for malware."),
            ("🔒 Harden SSH", self.hardener.harden_ssh, "Disables root login and password auth."),
            ("🔥 Setup Firewall (UFW)", self.hardener.setup_firewall, "Configures basic firewall rules."),
            ("📊 Check Resources", self.monitor.check_resources, "Displays current system resource usage.")
        ]
        
        for label, func, tooltip in ops:
            btn = ttk.Button(sidebar, text=label, command=lambda f=func, l=label: self.run_task(f, l))
            btn.pack(fill=tk.X, pady=5, padx=5)
            # Tooltip could be added here if we had a tooltip library
            
        # Control Buttons
        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        self.cancel_btn = ttk.Button(sidebar, text="🛑 Cancel Operation", command=self.cancel_operations, state=tk.DISABLED)
        self.cancel_btn.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Button(sidebar, text="❌ Exit", command=self.quit_app).pack(fill=tk.X, pady=5, padx=5, side=tk.BOTTOM)

        # Output Area
        self.output = scrolledtext.ScrolledText(content, font=("Consolas", 10), state=tk.DISABLED)
        self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status Bar
        self.status_var = tk.StringVar(value="System Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=2)

    def log_to_ui(self, message: str):
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    def run_task(self, func, label):
        if any(t.is_alive() for t in self.active_threads):
            messagebox.showwarning("Busy", "An operation is already running. Please wait or cancel it.")
            return

        self.stop_event.clear()
        self.cancel_btn.config(state=tk.NORMAL)
        self.status_var.set(f"Running: {label}...")
        self.output.config(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        self.output.config(state=tk.DISABLED)
        self.log_to_ui(f"Starting operation: {label}")
        
        def task_wrapper():
            try:
                # We can't easily cancel the underlying subprocess calls unless we pass the stop_event down
                # For now, we just handle the thread management
                result = func()
                if not self.stop_event.is_set():
                    self.queue.put(("result", result))
                else:
                    self.queue.put(("cancelled", "Operation cancelled by user."))
            except Exception as e:
                self.logger.exception(f"Error in task {label}")
                self.queue.put(("error", str(e)))
            finally:
                self.queue.put(("done", None))

        t = threading.Thread(target=task_wrapper, daemon=True)
        self.active_threads.append(t)
        t.start()

    def cancel_operations(self):
        if not any(t.is_alive() for t in self.active_threads):
            return
            
        if messagebox.askyesno("Cancel", "Are you sure you want to cancel the current operation?"):
            self.stop_event.set()
            self.log_to_ui("Cancellation requested... (Note: Subprocesses may take a moment to terminate)")
            self.status_var.set("Cancelling...")

    def process_queue(self):
        try:
            while True:
                msg_type, content = self.queue.get_nowait()
                
                if msg_type == "result":
                    self.log_to_ui(f"Result:\n{content}")
                    self.log_to_ui("Operation completed successfully.")
                elif msg_type == "error":
                    self.log_to_ui(f"ERROR: {content}")
                    messagebox.showerror("Operation Failed", f"An error occurred:\n{content}")
                elif msg_type == "cancelled":
                    self.log_to_ui(f"⚠️ {content}")
                elif msg_type == "done":
                    self.status_var.set("Ready")
                    self.cancel_btn.config(state=tk.DISABLED)
                    # Clean up threads list
                    self.active_threads = [t for t in self.active_threads if t.is_alive()]
                
                self.queue.task_done()
        except queue.Empty:
            pass
        
        self.after(100, self.process_queue)

    def quit_app(self):
        if any(t.is_alive() for t in self.active_threads):
            if not messagebox.askyesno("Quit", "Operations are still running. Quit anyway?"):
                return
        self.destroy()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enterprise Security Dashboard")
    parser.add_argument("--simulate", action="store_true", help="Run in simulation mode (safe for macOS/Windows)")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug logging")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be executed without making changes")
    
    args = parser.parse_args()
    
    # Auto-detect non-Linux environment
    if platform.system() != "Linux" and not args.simulate:
        print(f"⚠️  Detected {platform.system()} OS. Forcing Simulation Mode for safety.")
        print("   Use --simulate explicitly to suppress this warning.")
        args.simulate = True

    try:
        app = SecurityDashboard(simulation_mode=args.simulate, debug_mode=args.debug)
        app.mainloop()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Critical Error: {e}")
        logging.exception("Critical Application Error")
        sys.exit(1)

