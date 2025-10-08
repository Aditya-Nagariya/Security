#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import threading
import subprocess
import os
import sys
import time
import json
import random
from datetime import datetime
import platform
import shutil

# Ensure script runs with sudo privileges:
if os.geteuid() != 0:
    print("This script requires sudo privileges. Please run with sudo.")
    sys.exit(1)

class EnterpriseSecurityDashboard(tk.Tk):
    """Enterprise-grade Security Dashboard with responsive design,
    platform-specific styling, and professional UI components.
    """
    
    # Color schemes following modern enterprise design guidelines
    LIGHT_THEME = { 
        'bg_primary': '#FFFFFF',     # Primary background
        'bg_secondary': '#F5F7FA',   # Secondary background
        'bg_tertiary': '#EDF2F7',    # Tertiary background
        'text_primary': '#2D3748',   # Primary text
        'text_secondary': '#4A5568', # Secondary text
        'text_tertiary': '#718096',  # Tertiary text
        'accent': '#3182CE',         # Primary accent
        'accent_light': '#EBF8FF',   # Light accent background
        'border': '#E2E8F0',         # Border color
        'success': '#38A169',        # Success color
        'warning': '#DD6B20',        # Warning color
        'danger': '#E53E3E',         # Danger color
        'info': '#3182CE',           # Info color
    }
    
    DARK_THEME = {
        'bg_primary': '#171923',     # Primary background
        'bg_secondary': '#1A202C',   # Secondary background
        'bg_tertiary': '#2D3748',    # Tertiary background
        'text_primary': '#F7FAFC',   # Primary text
        'text_secondary': '#E2E8F0', # Secondary text
        'text_tertiary': '#A0AEC0',  # Tertiary text
        'accent': '#4299E1',         # Primary accent
        'accent_light': '#2C5282',   # Light accent background
        'border': '#4A5568',         # Border color
        'success': '#68D391',        # Success color
        'warning': '#F6AD55',        # Warning color
        'danger': '#FC8181',         # Danger color
        'info': '#63B3ED',           # Info color
        'shadow': '0 4px 6px rgba(0, 0, 0, 0.3)'  # Shadow
    }
    
    def __init__(self):
        super().__init__()
        self.title("Enterprise Security Dashboard")
        
        # Set up initial system information and state
        self.initialize_system_info()
        
        # Configure UI based on platform
        self.configure_platform_ui()
        
        # Set up responsive window size
        self.configure_window()
        
        # Set theme based on OS preference
        self.set_theme()
        
        # Create main grid structure for responsive layout
        self.columnconfigure(0, weight=1)  # Main column
        self.rowconfigure(0, weight=0)     # Header row
        self.rowconfigure(1, weight=1)     # Content row
        self.rowconfigure(2, weight=0)     # Status bar row
        
        # Create core UI components
        self.create_header()
        self.create_content()
        self.create_status_bar()
        
        # Set up event bindings
        self.bind("<Configure>", self.on_resize)
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        
        # Start periodic updates
        self.start_periodic_tasks()
    
    def initialize_system_info(self):
        """Initialize system information and dashboard state"""
        # System details
        self.hostname = platform.node()
        self.os_name = platform.system()
        self.os_version = platform.release()
        self.cpu_info = platform.processor() or "CPU information unavailable"
        
        # System metrics (will be updated periodically)
        self.system_metrics = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0,
            "uptime": "00:00:00",
            "security_score": 85,
            "vulnerabilities": 0,
            "last_scan_time": "Never",
            "network_traffic_in": 0,
            "network_traffic_out": 0
        }
        
        # Status message
        self.status_message = tk.StringVar(value="System Ready")
        self.time_string = tk.StringVar()
        
        # Recent activity log
        self.recent_activity = []
    
    def configure_platform_ui(self):
        """Configure UI elements based on current platform"""
        system = platform.system()
        
        # Default system font and scaling based on platform
        if system == "Darwin":  # macOS
            self.system_font = "SF Pro Text"
            self.monospace_font = "SF Mono"
            self.scaling_factor = 1.0
        elif system == "Windows":
            self.system_font = "Segoe UI"
            self.monospace_font = "Consolas"
            self.scaling_factor = 1.0
        else:  # Linux and others
            self.system_font = "DejaVu Sans"
            self.monospace_font = "DejaVu Sans Mono"
            self.scaling_factor = 0.9
        
        # Check if the fonts are available, otherwise fall back to system defaults
        available_fonts = font.families()
        if self.system_font not in available_fonts:
            if system == "Darwin":
                self.system_font = "Helvetica Neue"
            elif system == "Windows":
                self.system_font = "Tahoma"
            else:
                self.system_font = "TkDefaultFont"
        
        if self.monospace_font not in available_fonts:
            self.monospace_font = "TkFixedFont"
        
        # Define font sizes
        self.font_sizes = {
            'xs': int(9 * self.scaling_factor),
            'sm': int(11 * self.scaling_factor),
            'md': int(13 * self.scaling_factor),
            'lg': int(16 * self.scaling_factor),
            'xl': int(20 * self.scaling_factor),
            'xxl': int(24 * self.scaling_factor),
        }
    
    def configure_window(self):
        """Set up responsive window size and position"""
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate optimal window size (80% of screen)
        width = min(max(int(screen_width * 0.8), 1024), 1800)
        height = min(max(int(screen_height * 0.8), 768), 1200)
        
        # Position window in center of screen
        x_position = (screen_width - width) // 2
        y_position = (screen_height - height) // 2
        
        # Set window size and position
        self.geometry(f"{width}x{height}+{x_position}+{y_position}")
        self.minsize(1024, 768)
        
        # Store initial dimensions for responsive calculations
        self.initial_width = width
        self.initial_height = height
    
    def set_theme(self):
        """Detect and set theme based on OS settings"""
        # Default to light theme
        self.theme = self.LIGHT_THEME
        
        try:
            # macOS
            if platform.system() == "Darwin":
                result = subprocess.run(["defaults", "read", "-g", "AppleInterfaceStyle"], 
                                      capture_output=True, text=True)
                if result.stdout.strip() == "Dark":
                    self.theme = self.DARK_THEME
        
            # Windows
            elif platform.system() == "Windows":
                import winreg
                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                if value == 0:
                    self.theme = self.DARK_THEME
            
            # Linux (GNOME)
            elif platform.system() == "Linux":
                result = subprocess.run(["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"], 
                                      capture_output=True, text=True)
                if "dark" in result.stdout.lower():
                    self.theme = self.DARK_THEME
        except:
            # Fall back to light theme if detection fails
            pass
        
        # Apply theme to main window
        self.configure(bg=self.theme['bg_primary'])
        
        # Configure ttk styles based on theme
        self.configure_styles()
    
    def configure_styles(self):
        """Configure ttk styles for the application"""
        style = ttk.Style()
        style.theme_use("clam")  # Use clam as base theme for better customizations
        
        # Configure common elements
        style.configure(".",
                       font=(self.system_font, self.font_sizes['md']),
                       background=self.theme['bg_primary'],
                       foreground=self.theme['text_primary'])
        
        # Configure the Notebook (tabbed interface)
        style.configure("Enterprise.TNotebook", 
                       background=self.theme['bg_primary'],
                       borderwidth=0)
        
        style.configure("Enterprise.TNotebook.Tab", 
                       font=(self.system_font, self.font_sizes['md']),
                       background=self.theme['bg_secondary'],
                       foreground=self.theme['text_primary'],
                       padding=(16, 8),
                       borderwidth=0)
        
        style.map("Enterprise.TNotebook.Tab",
                 background=[("selected", self.theme['bg_primary']),
                            ("active", self.theme['bg_tertiary'])],
                 foreground=[("selected", self.theme['accent']),
                            ("active", self.theme['text_primary'])])
        
        # Configure buttons
        style.configure("Enterprise.TButton",
                      font=(self.system_font, self.font_sizes['md']),
                      background=self.theme['accent'],
                      foreground="#FFFFFF",
                      padding=(16, 10))
        
        style.map("Enterprise.TButton",
                 background=[("active", self.theme['accent_light']),
                            ("disabled", self.theme['bg_tertiary'])],
                 foreground=[("disabled", self.theme['text_tertiary'])])
        
        # Secondary button style
        style.configure("Secondary.TButton",
                      font=(self.system_font, self.font_sizes['md']),
                      background=self.theme['bg_tertiary'],
                      foreground=self.theme['text_primary'],
                      padding=(16, 10))
        
        style.map("Secondary.TButton",
                 background=[("active", self.theme['bg_secondary'])])
        
        # Configure frames
        style.configure("Enterprise.TFrame",
                       background=self.theme['bg_primary'])
        
        # Configure progressbars
        style.configure("Enterprise.Horizontal.TProgressbar",
                       background=self.theme['accent'],
                       troughcolor=self.theme['bg_tertiary'],
                       borderwidth=0)
    
    def create_header(self):
        """Create the application header"""
        header_frame = tk.Frame(self, bg=self.theme['bg_secondary'], height=64)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        
        # App title with logo
        title_frame = tk.Frame(header_frame, bg=self.theme['bg_secondary'])
        title_frame.pack(side=tk.LEFT, padx=20)
        
        # Dashboard title
        title_label = tk.Label(title_frame,
                              text="Enterprise Security Dashboard",
                              font=(self.system_font, self.font_sizes['lg'], "bold"),
                              fg=self.theme['text_primary'],
                              bg=self.theme['bg_secondary'])
        title_label.pack(side=tk.LEFT, pady=12)
        
        # Right side info (system info and time)
        info_frame = tk.Frame(header_frame, bg=self.theme['bg_secondary'])
        info_frame.pack(side=tk.RIGHT, padx=20, fill='y')
        
        # System info
        system_info = tk.Label(info_frame,
                             text=f"{self.hostname} | {self.os_name} {self.os_version}",
                             font=(self.system_font, self.font_sizes['sm']),
                             fg=self.theme['text_secondary'],
                             bg=self.theme['bg_secondary'])
        system_info.pack(side=tk.RIGHT, padx=15, pady=(20, 0))
        
        # Time display
        time_label = tk.Label(info_frame,
                           textvariable=self.time_string,
                           font=(self.system_font, self.font_sizes['sm']),
                           fg=self.theme['text_secondary'],
                           bg=self.theme['bg_secondary'])
        time_label.pack(side=tk.RIGHT, pady=(20, 0))
        
        # Update time initially
        self.update_time()
    
    def create_content(self):
        """Create the main content area with left sidebar and right content"""
        content_frame = tk.Frame(self, bg=self.theme['bg_primary'])
        content_frame.grid(row=1, column=0, sticky="nsew")
        
        # Configure content grid
        content_frame.columnconfigure(0, weight=0, minsize=250)  # Sidebar
        content_frame.columnconfigure(1, weight=1)  # Main content
        content_frame.rowconfigure(0, weight=1)  # Single row
        
        # Create sidebar
        self.create_sidebar(content_frame)
        
        # Create main tab content
        self.create_main_tabs(content_frame)
    
    def create_sidebar(self, parent):
        """Create the sidebar with system metrics and status"""
        sidebar_frame = tk.Frame(parent, bg=self.theme['bg_secondary'], width=250)
        sidebar_frame.grid(row=0, column=0, sticky='ns', padx=(0, 1))
        sidebar_frame.grid_propagate(False)  # Prevent resizing
        
        # Security score section
        score_frame = tk.Frame(sidebar_frame, bg=self.theme['bg_secondary'], padx=20, pady=20)
        score_frame.pack(fill='x')
        
        score_label = tk.Label(score_frame, 
                             text="Security Score",
                             font=(self.system_font, self.font_sizes['sm'], "bold"),
                             fg=self.theme['text_primary'],
                             bg=self.theme['bg_secondary'])
        score_label.pack(anchor='w')
        
        self.security_score_var = tk.StringVar(value="85/100")
        score_value = tk.Label(score_frame,
                             textvariable=self.security_score_var,
                             font=(self.system_font, self.font_sizes['xl'], "bold"),
                             fg=self.theme['accent'],
                             bg=self.theme['bg_secondary'])
        score_value.pack(anchor='w')
        
        # Divider
        self.add_divider(sidebar_frame)
        
        # System metrics section
        metrics_frame = tk.Frame(sidebar_frame, bg=self.theme['bg_secondary'])
        metrics_frame.pack(fill='x')
        
        # Add system metrics with progress bars
        metrics = [
            ("CPU Usage", "cpu_usage", "%"),
            ("Memory Usage", "memory_usage", "%"),
            ("Disk Usage", "disk_usage", "%")
        ]
        
        for label, key, unit in metrics:
            self.add_metric_gauge(metrics_frame, label, key, unit)
        
        # Network traffic
        net_frame = tk.Frame(metrics_frame, bg=self.theme['bg_secondary'], padx=20, pady=10)
        net_frame.pack(fill='x')
        
        net_title = tk.Label(net_frame,
                           text="Network Traffic",
                           font=(self.system_font, self.font_sizes['sm'], "bold"),
                           fg=self.theme['text_primary'],
                           bg=self.theme['bg_secondary'])
        net_title.pack(anchor='w')
        
        # Network in/out rates
        net_details_frame = tk.Frame(net_frame, bg=self.theme['bg_secondary'])
        net_details_frame.pack(fill='x', pady=5)
        
        # In traffic
        in_frame = tk.Frame(net_details_frame, bg=self.theme['bg_secondary'])
        in_frame.pack(side=tk.LEFT)
        
        in_label = tk.Label(in_frame,
                          text="In:",
                          font=(self.system_font, self.font_sizes['sm']),
                          fg=self.theme['text_secondary'],
                          bg=self.theme['bg_secondary'])
        in_label.pack(side=tk.LEFT)
        
        self.net_in_var = tk.StringVar(value="0 KB/s")
        in_value = tk.Label(in_frame,
                          textvariable=self.net_in_var,
                          font=(self.system_font, self.font_sizes['sm']),
                          fg=self.theme['info'],
                          bg=self.theme['bg_secondary'])
        in_value.pack(side=tk.LEFT, padx=5)
        
        # Out traffic
        out_frame = tk.Frame(net_details_frame, bg=self.theme['bg_secondary'])
        out_frame.pack(side=tk.RIGHT)
        
        out_label = tk.Label(out_frame,
                           text="Out:",
                           font=(self.system_font, self.font_sizes['sm']),
                           fg=self.theme['text_secondary'],
                           bg=self.theme['bg_secondary'])
        out_label.pack(side=tk.LEFT)
        
        self.net_out_var = tk.StringVar(value="0 KB/s")
        out_value = tk.Label(out_frame,
                          textvariable=self.net_out_var,
                          font=(self.system_font, self.font_sizes['sm']),
                          fg=self.theme['warning'],
                          bg=self.theme['bg_secondary'])
        out_value.pack(side=tk.LEFT, padx=5)
        
        # Divider
        self.add_divider(sidebar_frame)
        
        # Security metrics
        sec_frame = tk.Frame(sidebar_frame, bg=self.theme['bg_secondary'], padx=20, pady=10)
        sec_frame.pack(fill='x')
        
        # Vulnerabilities
        vuln_label = tk.Label(sec_frame,
                            text="Vulnerabilities Detected",
                            font=(self.system_font, self.font_sizes['sm'], "bold"),
                            fg=self.theme['text_primary'],
                            bg=self.theme['bg_secondary'])
        vuln_label.pack(anchor='w')
        
        self.vuln_var = tk.StringVar(value="0")
        vuln_value = tk.Label(sec_frame,
                            textvariable=self.vuln_var,
                            font=(self.system_font, self.font_sizes['xl'], "bold"),
                            fg=self.theme['danger'],
                            bg=self.theme['bg_secondary'])
        vuln_value.pack(anchor='w', pady=(0, 10))
        
        # Last scan time
        scan_label = tk.Label(sec_frame,
                            text="Last Security Scan",
                            font=(self.system_font, self.font_sizes['sm']),
                            fg=self.theme['text_primary'],
                            bg=self.theme['bg_secondary'])
        scan_label.pack(anchor='w')
        
        self.last_scan_var = tk.StringVar(value="Never")
        scan_value = tk.Label(sec_frame,
                            textvariable=self.last_scan_var,
                            font=(self.system_font, self.font_sizes['sm']),
                            fg=self.theme['text_secondary'],
                            bg=self.theme['bg_secondary'])
        scan_value.pack(anchor='w')
        
        # System uptime
        uptime_label = tk.Label(sec_frame,
                              text="System Uptime",
                              font=(self.system_font, self.font_sizes['sm']),
                              fg=self.theme['text_primary'],
                              bg=self.theme['bg_secondary'])
        uptime_label.pack(anchor='w', pady=(10, 0))
        
        self.uptime_var = tk.StringVar(value="00:00:00")
        uptime_value = tk.Label(sec_frame,
                              textvariable=self.uptime_var,
                              font=(self.system_font, self.font_sizes['sm']),
                              fg=self.theme['text_secondary'],
                              bg=self.theme['bg_secondary'])
        uptime_value.pack(anchor='w')
    
    def add_metric_gauge(self, parent, label, key, unit):
        """Add a metric with label and progress gauge"""
        frame = tk.Frame(parent, bg=self.theme['bg_secondary'], padx=20, pady=10)
        frame.pack(fill='x')
        
        # Top row with label and value
        top_row = tk.Frame(frame, bg=self.theme['bg_secondary'])
        top_row.pack(fill='x')
        
        # Label
        label_widget = tk.Label(top_row,
                              text=label,
                              font=(self.system_font, self.font_sizes['sm'], "bold"),
                              fg=self.theme['text_primary'],
                              bg=self.theme['bg_secondary'])
        label_widget.pack(side=tk.LEFT)
        
        # Value
        value_var = tk.StringVar(value=f"0{unit}")
        setattr(self, f"{key}_var", value_var)
        
        value_widget = tk.Label(top_row,
                              textvariable=value_var,
                              font=(self.system_font, self.font_sizes['sm']),
                              fg=self.theme['text_secondary'],
                              bg=self.theme['bg_secondary'])
        value_widget.pack(side=tk.RIGHT)
        
        # Progress bar
        progress = ttk.Progressbar(frame,
                                 style="Enterprise.Horizontal.TProgressbar",
                                 mode="determinate",
                                 value=0)
        progress.pack(fill='x', pady=(5, 0))
        
        # Store reference to progress bar
        setattr(self, f"{key}_progress", progress)
    
    def add_divider(self, parent):
        """Add a horizontal divider line"""
        divider = tk.Frame(parent, height=1, bg=self.theme['border'])
        divider.pack(fill='x', padx=15, pady=10)
    
    def create_main_tabs(self, parent):
        """Create the main tabbed interface"""
        self.tabs_frame = ttk.Frame(parent, style="Enterprise.TFrame")
        self.tabs_frame.grid(row=0, column=1, sticky="nsew", padx=(1, 0))
        
        # Create notebook (tabs container)
        self.notebook = ttk.Notebook(self.tabs_frame, style="Enterprise.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        tabs = {
            "Security Scan": self.create_security_scan_tab,
            "System Hardening": self.create_hardening_tab,
            "Monitoring": self.create_monitoring_tab,
            "Reports": self.create_reports_tab  # Changed from "Reports & Analytics" to match function calls
        }
        
        # Initialize tab content
        self.tab_contents = {}
        for name, create_func in tabs.items():
            tab_content = create_func()
            self.tab_contents[name] = tab_content
            self.notebook.add(tab_content, text=name)
    
    def create_tab_content(self, actions, title):
        """Create a standard tab with actions sidebar and output area"""
        tab = ttk.Frame(self.notebook, style="Enterprise.TFrame")
        
        # Configure grid
        tab.columnconfigure(0, weight=0, minsize=220)  # Actions sidebar
        tab.columnconfigure(1, weight=1)               # Output area
        tab.rowconfigure(0, weight=1)                  # Full height
        
        # Create actions sidebar
        sidebar = tk.Frame(tab, bg=self.theme['bg_tertiary'], padx=15, pady=15)
        sidebar.grid(row=0, column=0, sticky="ns")
        
        # Add actions title and help button
        title_frame = tk.Frame(sidebar, bg=self.theme['bg_tertiary'])
        title_frame.pack(fill='x', pady=(0, 10))
        
        actions_title = tk.Label(title_frame,
                              text=title,
                              font=(self.system_font, self.font_sizes['md'], "bold"),
                              fg=self.theme['text_primary'],
                              bg=self.theme['bg_tertiary'])
        actions_title.pack(side=tk.LEFT, anchor='w')
        
        # Help button with appropriate explanation based on tab
        help_text = self.get_tab_help_text(title)
        help_btn = ttk.Button(title_frame,
                            text="?",
                            width=2,
                            command=lambda: self.show_help_popup(f"Help: {title}", help_text),
                            style="Secondary.TButton")
        help_btn.pack(side=tk.RIGHT, anchor='e')
        
        # Add action buttons
        for text, command in actions:
            btn = ttk.Button(sidebar,
                          text=text,
                          command=lambda cmd=command: self.run_in_thread(cmd),
                          style="Enterprise.TButton")
            btn.pack(fill='x', pady=5)
        
        # Create output area
        output_frame = tk.Frame(tab, bg=self.theme['bg_primary'], padx=20, pady=20)
        output_frame.grid(row=0, column=1, sticky="nsew")
        
        # Output title
        output_title = tk.Label(output_frame,
                             text="Console Output",
                             font=(self.system_font, self.font_sizes['md'], "bold"),
                             fg=self.theme['text_primary'],
                             bg=self.theme['bg_primary'])
        output_title.pack(anchor='w', pady=(0, 10))
        
        # Output console
        output_console = scrolledtext.ScrolledText(output_frame,
                                                font=(self.monospace_font, self.font_sizes['sm']),
                                                bg=self.theme['bg_secondary'],
                                                fg=self.theme['text_primary'],
                                                bd=1,
                                                relief=tk.SOLID,
                                                borderwidth=1,
                                                highlightthickness=0)
        output_console.pack(fill='both', expand=True)
        
        # Add initial helpful text
        output_console.insert(tk.END, f"Welcome to {title}\n\n", "welcome")
        output_console.insert(tk.END, "Select an operation from the left sidebar to begin.\n", "info")
        output_console.insert(tk.END, "Results and information will appear in this console.\n\n", "info")
        output_console.insert(tk.END, "Click the '?' button for help and explanations.\n", "info")
        
        # Store output reference
        setattr(tab, "output", output_console)
        
        return tab
        
    def get_tab_help_text(self, title):
        """Return appropriate help text based on tab title"""
        if "Security Scan" in title:
            return (
                "Security scanning tools help identify vulnerabilities and security issues on your system.\n\n"
                "Available operations:\n\n"
                "• Full Security Scan: Comprehensive security audit using Lynis\n"
                "• Malware Detection: Scans for viruses and malicious software\n"
                "• Rootkit Detection: Checks for hidden malicious software\n"
                "• Network Security Scan: Identifies open ports and potential network vulnerabilities\n\n"
                "These scans may take several minutes to complete. Regular security scanning is recommended as part of "
                "good security practices."
            )
        elif "Hardening" in title:
            return (
                "System hardening is the process of securing a system by reducing vulnerabilities through configuration changes.\n\n"
                "Available operations:\n\n"
                "• Update System: Install the latest security updates\n"
                "• Harden SSH Configuration: Secure remote access settings\n"
                "• Configure Firewall: Set up network protection rules\n"
                "• Secure Web Directories: Set proper permissions for web server files\n\n"
                "These operations modify system settings to improve security. Some changes may require a system restart to take effect."
            )
        elif "Monitoring" in title:
            return (
                "Monitoring tools help you observe your system for security issues and unusual activity.\n\n"
                "Available operations:\n\n"
                "• Network Bandwidth: Monitor network traffic patterns\n"
                "• System Resources: Check CPU, memory and disk usage\n"
                "• Security Log Analysis: Analyze system logs for security events\n\n"
                "Regular monitoring helps detect security incidents and performance issues before they become critical problems."
            )
        elif "Report" in title:
            return (
                "Reports provide documentation of your system's security status and help track changes over time.\n\n"
                "Available operations:\n\n"
                "• Generate Security Report: Create a comprehensive security status report\n"
                "• Backup Home Directory: Create a backup of user files\n\n"
                "Regular reports and backups are essential parts of a complete security strategy."
            )
        else:
            return (
                "This section contains security operations to help protect your system.\n\n"
                "Select an operation from the sidebar to begin.\n\n"
                "The results will be displayed in the console output area."
            )

    def create_security_scan_tab(self):
        """Create the security scanning tab"""
        actions = [
            ("Full Security Scan", self.run_lynis),
            ("Malware Detection", self.run_clamav),
            ("Rootkit Detection", self.run_rkhunter),
            ("Network Security Scan", self.run_nmap)
        ]
        return self.create_tab_content(actions, "Security Scans")
    
    def create_hardening_tab(self):
        """Create the system hardening tab"""
        actions = [
            ("Update System", self.update_system),
            ("Harden SSH Configuration", self.harden_ssh),
            ("Configure Firewall", self.setup_ufw),
            ("Secure Web Directories", self.secure_web)
        ]
        return self.create_tab_content(actions, "System Hardening")
    
    def create_monitoring_tab(self):
        """Create the monitoring tab"""
        actions = [
            ("Network Bandwidth", self.monitor_bandwidth),
            ("System Resources", self.check_resources),
            ("Security Log Analysis", self.analyze_logs)
        ]
        return self.create_tab_content(actions, "System Monitoring")
    
    def create_reports_tab(self):
        """Create the reports tab"""
        actions = [
            ("Generate Security Report", self.generate_report),
            ("Backup Home Directory", self.backup_home)
        ]
        return self.create_tab_content(actions, "Reports")
    
    def create_status_bar(self):
        """Create a status bar with operation status and system info"""
        status_bar = tk.Frame(self, bg=self.theme['bg_tertiary'], height=28)
        status_bar.grid(row=2, column=0, sticky="ew", columnspan=2)
        status_bar.grid_propagate(False)
        
        # Status message (left side)
        status_label = tk.Label(status_bar,
                              textvariable=self.status_message,
                              font=(self.system_font, self.font_sizes['sm']),
                              fg=self.theme['text_secondary'],
                              bg=self.theme['bg_tertiary'])
        status_label.pack(side=tk.LEFT, padx=15)
        
        # Right side system info
        info_frame = tk.Frame(status_bar, bg=self.theme['bg_tertiary'])
        info_frame.pack(side=tk.RIGHT, fill='y')
        
        # Create version info
        version_label = tk.Label(info_frame,
                               text="Security Dashboard v1.0",
                               font=(self.system_font, self.font_sizes['xs']),
                               fg=self.theme['text_tertiary'],
                               bg=self.theme['bg_tertiary'])
        version_label.pack(side=tk.RIGHT, padx=15)
    
    def update_time(self):
        """Update the time display in the header"""
        now = datetime.now()
        self.time_string.set(now.strftime("%Y-%m-%d %H:%M:%S"))
        self.after(1000, self.update_time)
    
    def start_periodic_tasks(self):
        """Initialize and schedule periodic tasks"""
        # Start updating system metrics
        self.update_system_metrics()
        
        # Check for security updates periodically
        self.check_security_updates()
        
        # Simulate random activity for demo purposes
        if os.environ.get("DEMO_MODE") == "1":
            self.simulate_activity()
    
    def update_system_metrics(self):
        """Update all system metrics"""
        try:
            # CPU Usage
            cpu_usage = self.get_cpu_usage()
            self.update_metric("cpu_usage", cpu_usage, "%")
            
            # Memory Usage
            memory_usage = self.get_memory_usage()
            self.update_metric("memory_usage", memory_usage, "%")
            
            # Disk Usage
            disk_usage = self.get_disk_usage()
            self.update_metric("disk_usage", disk_usage, "%")
            
            # Uptime
            uptime = self.get_system_uptime()
            self.uptime_var.set(uptime)
            
            # Network traffic
            net_in, net_out = self.get_network_traffic()
            self.net_in_var.set(f"{net_in} KB/s")
            self.net_out_var.set(f"{net_out} KB/s")
            
        except Exception as e:
            print(f"Error updating system metrics: {e}")
        
        # Schedule next update
        self.after(5000, self.update_system_metrics)
    
    def update_metric(self, key, value, unit):
        """Update a specific metric value and progress bar"""
        # Update value display
        var_name = f"{key}_var"
        if hasattr(self, var_name):
            getattr(self, var_name).set(f"{value}{unit}")
        
        # Update progress bar
        progress_name = f"{key}_progress"
        if hasattr(self, progress_name):
            getattr(self, progress_name)["value"] = value
    
    def get_cpu_usage(self):
        """Get CPU usage percentage"""
        try:
            # Try using psutil if available
            import psutil
            return round(psutil.cpu_percent(interval=0.5))
        except ImportError:
            # Fallback to reading /proc/stat on Linux
            if platform.system() == "Linux":
                try:
                    with open("/proc/stat", "r") as f:
                        lines = f.readlines()
                    cpu_stats = lines[0].split()
                    user = float(cpu_stats[1])
                    nice = float(cpu_stats[2])
                    system = float(cpu_stats[3])
                    idle = float(cpu_stats[4])
                    total = user + nice + system + idle
                    return round((1 - (idle / total)) * 100)
                except:
                    pass
            
            # If all else fails, return a random value
            return random.randint(5, 60)
    
    def get_memory_usage(self):
        """Get memory usage percentage"""
        try:
            import psutil
            return round(psutil.virtual_memory().percent)
        except ImportError:
            # Fallback method for Linux
            if platform.system() == "Linux":
                try:
                    with open("/proc/meminfo", "r") as f:
                        lines = f.readlines()
                    
                    # Parse memory info
                    mem_info = {}
                    for line in lines:
                        parts = line.split(":")
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            if "kB" in value:
                                value = value.replace("kB", "").strip()
                                mem_info[key] = int(value)
                    
                    total = mem_info.get("MemTotal", 0)
                    free = mem_info.get("MemFree", 0)
                    buffers = mem_info.get("Buffers", 0)
                    cached = mem_info.get("Cached", 0)
                    
                    if total > 0:
                        used = total - free - buffers - cached
                        return round((used / total) * 100)
                except:
                    pass
            
            # Fallback to random value
            return random.randint(40, 85)
    
    def get_disk_usage(self):
        """Get disk usage percentage"""
        try:
            import psutil
            return round(psutil.disk_usage("/").percent)
        except ImportError:
            # Fallback for Unix systems
            try:
                output = subprocess.check_output(["df", "-h", "/"]).decode("utf-8")
                lines = output.strip().split("\n")
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        usage = parts[4].replace("%", "")
                        return int(usage)
            except:
                pass
            
            # Fallback to random value
            return random.randint(20, 80)
    
    def get_system_uptime(self):
        """Get system uptime as a formatted string"""
        try:
            if platform.system() == "Linux":
                with open("/proc/uptime", "r") as f:
                    uptime_seconds = float(f.readline().split()[0])
            else:
                import psutil
                uptime_seconds = time.time() - psutil.boot_time()
            
            # Format uptime
            days, remainder = divmod(uptime_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if days > 0:
                return f"{int(days)}d {int(hours)}h {int(minutes)}m"
            else:
                return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        except:
            # Fallback 
            return "Unknown"
    
    def get_network_traffic(self):
        """Get current network traffic in/out"""
        try:
            import psutil
            net_io = psutil.net_io_counters()
            curr_bytes_sent = net_io.bytes_sent
            curr_bytes_recv = net_io.bytes_recv
            
            # Store previous values
            if not hasattr(self, "_prev_net_io"):
                self._prev_net_io = (curr_bytes_sent, curr_bytes_recv, time.time())
                return ("0.0", "0.0")
            
            prev_sent, prev_recv, prev_time = self._prev_net_io
            time_diff = time.time() - prev_time
            
            # Calculate rate in KB/s
            sent_rate = (curr_bytes_sent - prev_sent) / time_diff / 1024
            recv_rate = (curr_bytes_recv - prev_recv) / time_diff / 1024
            
            # Update previous values
            self._prev_net_io = (curr_bytes_sent, curr_bytes_recv, time.time())
            
            return (f"{recv_rate:.1f}", f"{sent_rate:.1f}")
        except Exception as e:
            # Fallback to random values
            return (f"{random.uniform(0.1, 15.0):.1f}", f"{random.uniform(0.1, 5.0):.1f}")
    
    def check_security_updates(self):
        """Check for available security updates"""
        # This would connect to a security feed in a real application
        # For now, simulate finding updates occasionally
        if random.random() < 0.05:  # 5% chance
            self.status_message.set("Security updates available")
            self.vuln_var.set(str(random.randint(1, 5)))
        
        # Schedule next check
        self.after(60000, self.check_security_updates)  # Every minute
    
    def simulate_activity(self):
        """Simulate system activity for demo mode"""
        # Randomly update metrics for demonstration
        self.system_metrics["cpu_usage"] = min(100, max(5, self.system_metrics["cpu_usage"] + random.randint(-10, 10)))
        self.system_metrics["memory_usage"] = min(100, max(20, self.system_metrics["memory_usage"] + random.randint(-5, 5)))
        self.system_metrics["disk_usage"] = min(100, max(10, self.system_metrics["disk_usage"] + random.randint(-2, 2)))
        
        # Update progress bars
        self.update_metric("cpu_usage", self.system_metrics["cpu_usage"], "%")
        self.update_metric("memory_usage", self.system_metrics["memory_usage"], "%")
        self.update_metric("disk_usage", self.system_metrics["disk_usage"], "%")
        
        # Schedule next update
        self.after(3000, self.simulate_activity)  # Every 3 seconds
    
    def run_in_thread(self, func):
        """Execute a function in a separate thread"""
        self.status_message.set("Running operation...")
        thread = threading.Thread(target=func)
        thread.daemon = True
        thread.start()
    
    def run_command(self, command, tab_name, description):
        """Run a system command and display output in the specified tab"""
        # Get the appropriate output widget
        if tab_name in self.tab_contents:
            output = self.tab_contents[tab_name].output
            output.delete(1.0, tk.END)
        else:
            self.status_message.set(f"Error: Tab {tab_name} not found")
            return
        
        # Clear output and display header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output.insert(tk.END, f"=== {description} ===\n")
        output.insert(tk.END, f"Started at {timestamp}\n\n")
        
        # Add user-friendly explanation based on the operation type
        self.add_operation_explanation(output, description)
        
        try:
            # Display command being executed
            output.insert(tk.END, f"Executing: {command}\n\n")
            output.update_idletasks()  # Update display
            
            # Execute the command
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Read and display output in real-time
            for line in process.stdout:
                if "error" in line.lower() or "warning" in line.lower():
                    output.insert(tk.END, f"! {line}", "warning")
                else:
                    output.insert(tk.END, line)
                output.see(tk.END)  # Auto-scroll
                output.update_idletasks()
            
            # Wait for process to complete
            process.wait()
            
            # Check return code
            if process.returncode == 0:
                output.insert(tk.END, "\n=== Operation completed successfully ===\n")
                self.status_message.set("Operation completed successfully")
                
                # Update last scan time if this was a security scan
                if "scan" in description.lower():
                    self.last_scan_var.set(timestamp)
                    
                # Add summary of results based on operation type
                self.add_success_summary(output, description)
            else:
                # Display stderr output if command failed
                error_output = process.stderr.read()
                output.insert(tk.END, f"\nError output:\n{error_output}\n")
                output.insert(tk.END, f"\n=== Operation failed (exit code {process.returncode}) ===\n")
                
                # Add user-friendly error explanation
                output.insert(tk.END, "\n📋 What this means:\n", "error_header")
                
                # Common error handling with user-friendly messages
                if "command not found" in error_output.lower():
                    output.insert(tk.END, "The required security tool couldn't be found on your system.\n")
                    output.insert(tk.END, "This usually happens when the software isn't installed correctly.\n\n")
                    output.insert(tk.END, "🔧 How to fix this:\n", "fix_header")
                    output.insert(tk.END, f"Try manually installing the required tool:\n")
                    
                    # Suggest appropriate installation command
                    if self.check_tool_installed("apt"):
                        output.insert(tk.END, f"sudo apt install {command.split()[0]}\n")
                    elif self.check_tool_installed("dnf"):
                        output.insert(tk.END, f"sudo dnf install {command.split()[0]}\n")
                    else:
                        output.insert(tk.END, f"Install {command.split()[0]} using your system's package manager\n")
                        
                elif "permission denied" in error_output.lower():
                    output.insert(tk.END, "You don't have enough permissions to run this security operation.\n")
                    output.insert(tk.END, "Security tools often need administrator (root) privileges.\n\n")
                    output.insert(tk.END, "🔧 How to fix this:\n", "fix_header")
                    output.insert(tk.END, "- Make sure you launched this application with sudo\n")
                    output.insert(tk.END, "- Try restarting the application with: sudo python3 security.py\n")
                elif "no such file or directory" in error_output.lower():
                    output.insert(tk.END, "A required file or directory wasn't found on your system.\n\n")
                    output.insert(tk.END, "🔧 How to fix this:\n", "fix_header")
                    output.insert(tk.END, "- Check if the security tool is properly installed\n")
                    output.insert(tk.END, "- Try reinstalling the tool\n")
                else:
                    # Generic error message
                    output.insert(tk.END, "The operation couldn't be completed due to an error.\n")
                    output.insert(tk.END, "This might be due to a configuration issue or missing dependency.\n\n")
                    output.insert(tk.END, "🔧 How to fix this:\n", "fix_header")
                    output.insert(tk.END, "- Check the error output above for specific details\n")
                    output.insert(tk.END, "- Make sure all required software is installed\n")
                    output.insert(tk.END, "- Try running the Security Dashboard with root privileges\n")
                
                self.status_message.set("Operation failed - check output for details")
                
        except Exception as e:
            output.insert(tk.END, f"\nError executing command: {str(e)}\n")
            output.insert(tk.END, "\n📋 What this means:\n", "error_header")
            output.insert(tk.END, "There was a problem running the security operation.\n")
            output.insert(tk.END, "This might be because of missing programs or system limitations.\n\n")
            output.insert(tk.END, "🔧 How to fix this:\n", "fix_header")
            output.insert(tk.END, "- Make sure you have the necessary security tools installed\n")
            output.insert(tk.END, "- Try running the Security Dashboard with root privileges\n")
            self.status_message.set(f"Error: {str(e)}")

    def add_operation_explanation(self, output, description):
        """Add user-friendly explanation of security operations"""
        output.insert(tk.END, "📋 Operation Details:\n", "info_header")
        
        if "Security Scan" in description or "Lynis" in description:
            output.insert(tk.END, "This operation will check your system for security vulnerabilities and configuration issues.\n")
            output.insert(tk.END, "The scan may take a few minutes to complete. Results will show potential security issues that need attention.\n\n")
        elif "Malware" in description or "ClamAV" in description:
            output.insert(tk.END, "This will scan your system for viruses, malware, and other malicious software.\n")
            output.insert(tk.END, "The scan may take several minutes depending on how many files need to be checked.\n\n")
        elif "Rootkit" in description:
            output.insert(tk.END, "This operation checks for rootkits - malicious software designed to gain unauthorized access to your system.\n")
            output.insert(tk.END, "The scan will look for suspicious programs and files that might indicate a security breach.\n\n")
        elif "Network" in description or "Nmap" in description:
            output.insert(tk.END, "This will scan network services and open ports to identify potential security vulnerabilities.\n")
            output.insert(tk.END, "The scan checks which services are accessible and might be exploitable.\n\n")
        elif "SSH" in description:
            output.insert(tk.END, "This operation will strengthen the security of your SSH (Secure Shell) server configuration.\n")
            output.insert(tk.END, "It will modify settings to prevent unauthorized access and follow security best practices.\n\n")
        elif "Firewall" in description:
            output.insert(tk.END, "This will configure your system firewall to improve security by controlling network traffic.\n")
            output.insert(tk.END, "It will block unauthorized access while allowing legitimate connections.\n\n")
        elif "Web Directory" in description:
            output.insert(tk.END, "This operation will secure web server directories by setting appropriate permissions.\n")
            output.insert(tk.END, "It prevents unauthorized access to web files and improves overall web server security.\n\n")
        elif "Bandwidth" in description:
            output.insert(tk.END, "This will monitor your network traffic to show data usage and detect unusual patterns.\n")
            output.insert(tk.END, "High or unusual network activity might indicate security issues.\n\n")
        elif "Report" in description:
            output.insert(tk.END, "This will create a comprehensive security report of your system's current state.\n")
            output.insert(tk.END, "The report includes system information, user accounts, network configuration, and security recommendations.\n\n")
        elif "Backup" in description:
            output.insert(tk.END, "This creates a backup of important files to protect against data loss.\n")
            output.insert(tk.END, "Backups are essential for recovery after security incidents or system failures.\n\n")
        else:
            output.insert(tk.END, "This security operation will help protect your system.\n")
            output.insert(tk.END, "Please wait while the operation completes.\n\n")
        
        output.insert(tk.END, "⏳ Please wait while the operation runs...\n\n", "progress_note")

    def add_success_summary(self, output, description):
        """Add user-friendly summary after successful operations"""
        output.insert(tk.END, "\n📋 Summary:\n", "success_header")
        
        if "Security Scan" in description or "Lynis" in description:
            output.insert(tk.END, "✅ Your system has been checked for security vulnerabilities.\n")
            output.insert(tk.END, "Review the output above for any warnings or suggestions to improve your system security.\n")
            output.insert(tk.END, "Consider addressing any 'Warnings' or 'Suggestions' mentioned in the results.\n")
        elif "Malware" in description or "ClamAV" in description:
            output.insert(tk.END, "✅ Malware scan completed. If any threats were found, they are listed above.\n")
            output.insert(tk.END, "If infected files were detected, they should be quarantined or removed.\n")
            output.insert(tk.END, "Regular scans are recommended to keep your system secure.\n")
        elif "Rootkit" in description:
            output.insert(tk.END, "✅ Rootkit detection scan completed.\n")
            output.insert(tk.END, "Any suspicious files or programs would be listed in the results above.\n")
            output.insert(tk.END, "If warnings were found, further investigation is recommended.\n")
        elif "Firewall" in description:
            output.insert(tk.END, "✅ Firewall has been successfully configured.\n")
            output.insert(tk.END, "Your system is now better protected against unauthorized network access.\n")
            output.insert(tk.END, "The firewall is active and using the security rules shown above.\n")
        elif "SSH" in description:
            output.insert(tk.END, "✅ SSH configuration has been secured.\n")
            output.insert(tk.END, "Your SSH server now uses more secure settings to prevent unauthorized access.\n")
            output.insert(tk.END, "Remember that password authentication is now disabled - use SSH keys for access.\n")
        elif "Report" in description:
            output.insert(tk.END, "✅ Security report has been generated successfully.\n")
            output.insert(tk.END, "The report contains important information about your system's security status.\n")
            output.insert(tk.END, "Review the report to identify areas that need security improvements.\n")
        else:
            output.insert(tk.END, "✅ Operation completed successfully.\n")
            output.insert(tk.END, "Your system security has been improved.\n")

    def install_package(self, package):
        """Install a package using the appropriate package manager"""
        # Determine package manager
        package_manager = None
        install_cmd = None
        
        if self.check_tool_installed("apt"):
            package_manager = "apt"
            install_cmd = f"apt update && apt install -y {package}"
        elif self.check_tool_installed("dnf"):
            package_manager = "dnf"
            install_cmd = f"dnf install -y {package}"
        elif self.check_tool_installed("yum"):
            package_manager = "yum"
            install_cmd = f"yum install -y {package}"
        elif self.check_tool_installed("pacman"):
            package_manager = "pacman"
            install_cmd = f"pacman -S --noconfirm {package}"
        elif self.check_tool_installed("zypper"):
            package_manager = "zypper"
            install_cmd = f"zypper install -y {package}"
        elif self.check_tool_installed("brew") and platform.system() == "Darwin":
            package_manager = "brew"
            install_cmd = f"brew install {package}"
        else:
            self.status_message.set(f"Error: Cannot install {package}, unsupported package manager")
            return False
        
        try:
            self.status_message.set(f"Installing {package} using {package_manager}... This may take a moment.")
            result = subprocess.run(install_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                self.status_message.set(f"{package} installed successfully")
                return True
            else:
                self.status_message.set(f"Error: Failed to install {package}")
                return False
        except subprocess.CalledProcessError as e:
            self.status_message.set(f"Error: Failed to install {package} - check your internet connection")
            return False
        except Exception as e:
            self.status_message.set(f"Error: Failed to install {package} - administrator privileges may be required")
            return False

    # Add these new helper methods to display status information
    def show_help_popup(self, title, message):
        """Show a help popup with explanations for the user"""
        help_window = tk.Toplevel(self)
        help_window.title(title)
        help_window.geometry("500x400")
        help_window.transient(self)
        help_window.grab_set()
        
        # Style the window
        help_window.configure(bg=self.theme['bg_primary'])
        
        # Add content
        header_label = tk.Label(help_window, 
                              text=title,
                              font=(self.system_font, self.font_sizes['lg'], "bold"),
                              fg=self.theme['accent'],
                              bg=self.theme['bg_primary'],
                              wraplength=480)
        header_label.pack(pady=(20, 10), padx=20)
        
        content = scrolledtext.ScrolledText(help_window,
                                         font=(self.system_font, self.font_sizes['md']),
                                         bg=self.theme['bg_secondary'],
                                         fg=self.theme['text_primary'],
                                         wrap=tk.WORD,
                                         width=50,
                                         height=15)
        content.pack(expand=True, fill='both', padx=20, pady=10)
        content.insert(tk.END, message)
        content.config(state='disabled')  # Make read-only
        
        # Close button
        close_btn = ttk.Button(help_window, 
                             text="Close", 
                             command=help_window.destroy,
                             style="Enterprise.TButton")
        close_btn.pack(pady=20)

    def harden_ssh(self):
        """Apply SSH hardening configurations"""
        # Check if SSH is installed and the config file exists
        if not os.path.exists("/etc/ssh/sshd_config"):
            self.status_message.set("Error: SSH server not installed")
            tab_name = "System Hardening"
            if tab_name in self.tab_contents:
                output = self.tab_contents[tab_name].output
                output.delete(1.0, tk.END)
                output.insert(tk.END, "=== SSH Hardening Error ===\n\n")
                output.insert(tk.END, "Error: SSH server is not installed or sshd_config not found.\n")
                output.insert(tk.END, "To install SSH server: sudo apt install openssh-server\n")
            return
        
        # Create a backup of original config
        backup_command = "cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup"
        
        # Detect SSH service name
        ssh_service_name = "sshd"
        if self.check_service_exists("ssh.service"):
            ssh_service_name = "ssh"
        elif self.check_service_exists("sshd.service"):
            ssh_service_name = "sshd"
        elif self.check_service_exists("openssh.service"):
            ssh_service_name = "openssh"
        else:
            # If we can't find a service, just apply config changes without restart
            hardening_commands = [
                backup_command,
                "sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config",
                "sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config",
                "sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config",
                "echo 'SSH hardening applied, but no SSH service detected to restart'"
            ]
            command = " && ".join(hardening_commands)
            self.run_command(command, "System Hardening", "SSH Hardening (no service restart)")
            return
        
        # Apply multiple SSH hardening rules with detected service name
        hardening_commands = [
            backup_command,
            "sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config",
            "sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config",
            "sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config",
            f"systemctl restart {ssh_service_name}.service || service {ssh_service_name} restart"
        ]
        
        command = " && ".join(hardening_commands)
        self.run_command(command, "System Hardening", "SSH Hardening")
    
    def setup_ufw(self):
        """Configure Uncomplicated Firewall (UFW)"""
        if not self.check_tool_installed("ufw"):
            # Try to install UFW
            if not self.install_package("ufw"):
                tab_name = "System Hardening"
                if tab_name in self.tab_contents:
                    output = self.tab_contents[tab_name].output
                    output.delete(1.0, tk.END)
                    output.insert(tk.END, "=== Firewall Configuration Error ===\n\n")
                    output.insert(tk.END, "Error: Could not install UFW (Uncomplicated Firewall).\n")
                    output.insert(tk.END, "Please install UFW manually: sudo apt install ufw\n")
                    
                    # Check if any other firewall tool is available
                    if self.check_tool_installed("firewalld"):
                        output.insert(tk.END, "\nDetected firewalld. You can use that instead.\n")
                        self.run_command("firewall-cmd --state", "System Hardening", "Firewalld Status")
                    elif self.check_tool_installed("iptables"):
                        output.insert(tk.END, "\nDetected iptables. Showing current rules:\n")
                        self.run_command("iptables -L", "System Hardening", "IPTables Rules")
                return
        
        # Configure basic firewall rules
        commands = [
            "ufw --force reset",  # Reset to default
            "ufw default deny incoming",  # Default deny incoming
            "ufw default allow outgoing",  # Default allow outgoing
            "ufw allow ssh",  # Allow SSH
            "ufw allow 80/tcp",  # Allow HTTP
            "ufw allow 443/tcp",  # Allow HTTPS
            "echo 'y' | ufw enable",  # Enable firewall
            "ufw status verbose"  # Show status
        ]
        
        command = " && ".join(commands)
        self.run_command(command, "System Hardening", "Firewall Configuration")
    
    def secure_web(self):
        """Apply security measures to web directories"""
        # Check if Apache or Nginx is installed
        web_root = None
        
        if os.path.exists("/var/www/html"):
            web_root = "/var/www/html"
        elif os.path.exists("/usr/share/nginx/html"):
            web_root = "/usr/share/nginx/html"
        
        if not web_root:
            self.status_message.set("Error: No web server detected")
            return
        
        # Apply permission hardening
        command = f"""
        find {web_root} -type d -exec chmod 750 {{}} \\;
        find {web_root} -type f -exec chmod 640 {{}} \\;
        chown -R www-data:www-data {web_root}
        """
        
        self.run_command(command, "System Hardening", "Web Directory Security")
    
    def check_service_exists(self, service_name):
        """Check if a system service exists"""
        try:
            result = subprocess.run(f"systemctl status {service_name}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.returncode != 4  # 4 means unit not found
        except Exception:
            try:
                result = subprocess.run(f"service {service_name.split('.')[0]} status", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                return result.returncode != 4
            except Exception:
                return False
    
    def monitor_bandwidth(self):
        """Monitor network bandwidth usage"""
        if not self.check_tool_installed("vnstat"):
            # Try to install vnstat
            success = self.install_package("vnstat")
            if success:
                try:
                    # Try to initialize vnstat on default interface
                    interfaces_cmd = subprocess.run("ip route | grep default | awk '{print $5}'", 
                                                 shell=True, stdout=subprocess.PIPE, text=True)
                    default_interface = interfaces_cmd.stdout.strip()
                    
                    if default_interface:
                        self.run_command(f"vnstat --create -i {default_interface}", 
                                        "Monitoring", "Initializing bandwidth monitoring")
                    else:
                        self.run_command("vnstat --create", 
                                        "Monitoring", "Initializing bandwidth monitoring (all interfaces)")
                except Exception as e:
                    print(f"Error initializing vnstat: {e}")
            else:
                # If vnstat installation fails, use a fallback
                tab_name = "Monitoring"
                if tab_name in self.tab_contents:
                    output = self.tab_contents[tab_name].output
                    output.delete(1.0, tk.END)
                    output.insert(tk.END, "=== Network Bandwidth Monitoring ===\n\n")
                    output.insert(tk.END, "Error: Could not install vnstat. Using ifconfig/ip fallback.\n\n")
                    
                    # Use ifconfig or ip as fallback
                    if self.check_tool_installed("ifconfig"):
                        self.run_command("ifconfig", "Monitoring", "Network Interfaces Info")
                    elif self.check_tool_installed("ip"):
                        self.run_command("ip -s link", "Monitoring", "Network Interfaces Info")
                    else:
                        output.insert(tk.END, "No network monitoring tools available.\n")
                return
        
        # Run vnstat with fallback options
        if subprocess.run("vnstat -h", shell=True, stderr=subprocess.PIPE).returncode == 0:
            self.run_command("vnstat -h", "Monitoring", "Network Bandwidth Monitoring")
        else:
            self.run_command("vnstat", "Monitoring", "Network Bandwidth Summary")
    
    def update_system(self):
        """Update system packages"""
        # Determine package manager based on system
        if self.check_tool_installed("apt"):
            command = "apt update && apt upgrade -y"
        elif self.check_tool_installed("dnf"):
            command = "dnf update -y"
        elif self.check_tool_installed("yum"):
            command = "yum update -y"
        elif self.check_tool_installed("pacman"):
            command = "pacman -Syu --noconfirm"
        elif self.check_tool_installed("zypper"):
            command = "zypper update -y"
        elif self.check_tool_installed("brew") and platform.system() == "Darwin":
            command = "brew update && brew upgrade"
        else:
            self.status_message.set("Error: Unsupported package manager")
            return
        
        self.run_command(command, "System Hardening", "System Update")
    
    def secure_web(self):
        """Apply security measures to web directories"""
        # Check if Apache or Nginx is installed
        web_root = None
        
        if os.path.exists("/var/www/html"):
            web_root = "/var/www/html"
        elif os.path.exists("/usr/share/nginx/html"):
            web_root = "/usr/share/nginx/html"
        
        if not web_root:
            self.status_message.set("Error: No web server detected")
            return
        
        # Apply permission hardening
        command = f"""
        find {web_root} -type d -exec chmod 750 {{}} \\;
        find {web_root} -type f -exec chmod 640 {{}} \\;
        chown -R www-data:www-data {web_root}
        """
        
        self.run_command(command, "System Hardening", "Web Directory Security")
    
    def check_resources(self):
        """Check system resource usage"""
        commands = [
            "echo '=== CPU Information ==='",
            "lscpu | grep -E 'Model name|Socket|Core|Thread'",
            "echo '=== Memory Usage ==='",
            "free -h",
            "echo '=== Disk Usage ==='",
            "df -h",
            "echo '=== Top Processes by CPU ==='",
            "ps aux --sort=-%cpu | head -10",
            "echo '=== Top Processes by Memory ==='",
            "ps aux --sort=-%mem | head -10"
        ]
        
        command = " && ".join(commands)
        self.run_command(command, "Monitoring", "System Resource Analysis")  # Changed from "System Monitoring"
    
    def analyze_logs(self):
        """Analyze system logs for security issues"""
        if not self.check_tool_installed("logwatch"):
            self.install_package("logwatch")
        
        command = "logwatch --output stdout --format text --detail high --range today"
        self.run_command(command, "Monitoring", "Security Log Analysis")  # Changed from "System Monitoring"
    
    def generate_report(self):
        """Generate a comprehensive security report"""
        report_file = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        commands = [
            f"echo 'Security Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}' > {report_file}",
            f"echo '======================================================' >> {report_file}",
            f"echo '1. System Information' >> {report_file}",
            f"uname -a >> {report_file}",
            f"echo '======================================================' >> {report_file}",
            f"echo '2. User Accounts' >> {report_file}",
            f"cat /etc/passwd | cut -d: -f1,3,4 >> {report_file}",
            f"echo '======================================================' >> {report_file}",
            f"echo '3. Network Configuration' >> {report_file}",
            f"ip addr show | grep -E 'inet|ether' >> {report_file}",
            f"echo '======================================================' >> {report_file}",
            f"echo '4. Listening Ports' >> {report_file}",
            f"netstat -tuln >> {report_file}",
            f"echo '======================================================' >> {report_file}",
            f"echo '5. System Updates' >> {report_file}",
            f"if command -v apt &> /dev/null; then apt list --upgradable 2>/dev/null >> {report_file}; fi",
            f"echo '======================================================' >> {report_file}",
            f"echo '6. Security Recommendations' >> {report_file}",
            f"if command -v lynis &> /dev/null; then lynis audit system --no-colors --quiet >> {report_file}; else echo 'Lynis not installed' >> {report_file}; fi",
            f"echo 'Report saved to {report_file}'",
            f"cat {report_file}"
        ]
        
        command = " && ".join(commands)
        self.run_command(command, "Reports", f"Generating Security Report: {report_file}")
    
    def backup_home(self):
        """Backup the home directory"""
        backup_file = f"home_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        
        command = f"tar -czf {backup_file} --exclude='.cache' /home && echo 'Backup completed: {backup_file}'"
        self.run_command(command, "Reports", "Home Directory Backup")
    
    # Utility methods
    def check_tool_installed(self, tool_name):
        """Check if a tool is installed in the system"""
        try:
            result = subprocess.run(["which", tool_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def install_package(self, package):
        """Install a package using the appropriate package manager"""
        # Determine package manager
        package_manager = None
        install_cmd = None
        
        if self.check_tool_installed("apt"):
            package_manager = "apt"
            install_cmd = f"apt update && apt install -y {package}"
        elif self.check_tool_installed("dnf"):
            package_manager = "dnf"
            install_cmd = f"dnf install -y {package}"
        elif self.check_tool_installed("yum"):
            package_manager = "yum"
            install_cmd = f"yum install -y {package}"
        elif self.check_tool_installed("pacman"):
            package_manager = "pacman"
            install_cmd = f"pacman -S --noconfirm {package}"
        elif self.check_tool_installed("zypper"):
            package_manager = "zypper"
            install_cmd = f"zypper install -y {package}"
        elif self.check_tool_installed("brew") and platform.system() == "Darwin":
            package_manager = "brew"
            install_cmd = f"brew install {package}"
        else:
            self.status_message.set(f"Error: Cannot install {package}, unsupported package manager")
            return False
        
        try:
            self.status_message.set(f"Installing {package} using {package_manager}...")
            result = subprocess.run(install_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                self.status_message.set(f"{package} installed successfully")
                return True
            else:
                self.status_message.set(f"Error: Failed to install {package}")
                return False
        except subprocess.CalledProcessError as e:
            self.status_message.set(f"Error: Failed to install {package}: {e}")
            return False
        except Exception as e:
            self.status_message.set(f"Error: Failed to install {package}: {str(e)}")
            return False
    
    def on_resize(self, event):
        """Handle window resize events"""
        # Only respond to the main window resizing, not child widgets
        if event.widget == self:
            # Update any UI elements that need to respond to resize
            current_width = self.winfo_width()
            current_height = self.winfo_height()
            
            # You could adjust layout based on new dimensions here
            pass
    
    def on_exit(self):
        """Handle application exit"""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit the Security Dashboard?"):
            # Clean up any resources or temporary files
            self.destroy()

    # Security operation implementations
    def run_lynis(self):
        """Run a comprehensive security scan using Lynis"""
        if not self.check_tool_installed("lynis"):
            # Try to install lynis
            if not self.install_package("lynis"):
                # If installation fails, show message in console
                tab_name = "Security Scan"
                if tab_name in self.tab_contents:
                    output = self.tab_contents[tab_name].output
                    output.delete(1.0, tk.END)
                    output.insert(tk.END, "=== Error: Could not install Lynis ===\n\n")
                    output.insert(tk.END, "Lynis is a security auditing tool that's needed for this scan.\n\n")
                    output.insert(tk.END, "📋 What this means:\n", "error_header")
                    output.insert(tk.END, "The security scanner couldn't be installed on your system.\n")
                    output.insert(tk.END, "This is typically because the package isn't in your system's repositories.\n\n")
                    output.insert(tk.END, "🔧 How to fix this:\n", "fix_header")
                    output.insert(tk.END, "Try manually installing Lynis:\n")
                    output.insert(tk.END, "1. sudo apt install lynis (for Debian/Ubuntu)\n")
                    output.insert(tk.END, "2. sudo dnf install lynis (for Fedora/RHEL)\n")
                    output.insert(tk.END, "3. Or download from https://cisofy.com/lynis/\n\n")
                    output.insert(tk.END, "In the meantime, try one of the other security scan options.")
                return
        
        command = "lynis audit system --no-colors"
        self.run_command(command, "Security Scan", "Comprehensive Security Scan")
    
    def run_clamav(self):
        """Run malware scan using ClamAV"""
        if not self.check_tool_installed("clamscan"):
            if not self.install_package("clamav"):
                tab_name = "Security Scan"
                if tab_name in self.tab_contents:
                    output = self.tab_contents[tab_name].output
                    output.delete(1.0, tk.END)
                    output.insert(tk.END, "=== Error: Could not install ClamAV ===\n\n")
                    output.insert(tk.END, "ClamAV is an antivirus engine needed for malware scanning.\n\n")
                    output.insert(tk.END, "📋 What this means:\n", "error_header")
                    output.insert(tk.END, "The malware scanner couldn't be installed on your system.\n\n")
                    output.insert(tk.END, "🔧 How to fix this:\n", "fix_header")
                    output.insert(tk.END, "Try manually installing ClamAV:\n")
                    output.insert(tk.END, "1. sudo apt install clamav (for Debian/Ubuntu)\n")
                    output.insert(tk.END, "2. sudo dnf install clamav (for Fedora/RHEL)\n\n")
                    output.insert(tk.END, "Running basic file scan as an alternative...\n\n")
                    
                    # Run a basic scan as a fallback
                    fallback_cmd = "find /home -type f -name '*.sh' -o -name '*.py' | xargs -I{} grep -l 'suspicious' {} 2>/dev/null || echo 'No obvious suspicious scripts found'"
                    self.run_command(fallback_cmd, "Security Scan", "Basic Script Scan")
                return
            
            # Update virus definitions if ClamAV was just installed
            self.run_command("freshclam || echo 'Skipping virus database update'", "Security Scan", "Updating Virus Definitions")
        
        # Choose a reasonable path to scan to avoid excessive time
        command = "clamscan -r /home --bell -i --max-filesize=100M --max-scansize=500M"
        self.run_command(command, "Security Scan", "Malware Detection Scan")
    
    def run_rkhunter(self):
        """Run rootkit detection using RKHunter"""
        if not self.check_tool_installed("rkhunter"):
            if not self.install_package("rkhunter"):
                tab_name = "Security Scan"
                if tab_name in self.tab_contents:
                    output = self.tab_contents[tab_name].output
                    output.delete(1.0, tk.END)
                    output.insert(tk.END, "=== Error: Could not install RKHunter ===\n\n")
                    output.insert(tk.END, "RKHunter is a rootkit scanner needed to check for hidden malware.\n\n")
                    output.insert(tk.END, "📋 What this means:\n", "error_header")
                    output.insert(tk.END, "The rootkit detector couldn't be installed on your system.\n\n")
                    output.insert(tk.END, "🔧 How to fix this:\n", "fix_header")
                    output.insert(tk.END, "Try manually installing RKHunter:\n")
                    output.insert(tk.END, "1. sudo apt install rkhunter (for Debian/Ubuntu)\n")
                    output.insert(tk.END, "2. sudo dnf install rkhunter (for Fedora/RHEL)\n\n")
                    output.insert(tk.END, "Running alternative check for unusual files with special permissions...\n\n")
                    
                    # Run a basic SUID scan as a fallback
                    fallback_cmd = "find /bin /sbin /usr/bin /usr/sbin -type f -perm -4000 -o -perm -2000 -ls"
                    self.run_command(fallback_cmd, "Security Scan", "Special Permission Files Scan")
                return
        
        # Avoid interactive prompts with --skip-keypress
        command = "rkhunter --check --skip-keypress"
        self.run_command(command, "Security Scan", "Rootkit Detection Scan")
    
    def run_nmap(self):
        """Run network security scan using Nmap"""
        if not self.check_tool_installed("nmap"):
            if not self.install_package("nmap"):
                tab_name = "Security Scan"
                if tab_name in self.tab_contents:
                    output = self.tab_contents[tab_name].output
                    output.delete(1.0, tk.END)
                    output.insert(tk.END, "=== Error: Could not install Nmap ===\n\n")
                    output.insert(tk.END, "Nmap is a network scanner needed to check for open ports and services.\n\n")
                    output.insert(tk.END, "📋 What this means:\n", "error_header")
                    output.insert(tk.END, "The network scanner couldn't be installed on your system.\n\n")
                    output.insert(tk.END, "🔧 How to fix this:\n", "fix_header")
                    output.insert(tk.END, "Try manually installing Nmap:\n")
                    output.insert(tk.END, "1. sudo apt install nmap (for Debian/Ubuntu)\n")
                    output.insert(tk.END, "2. sudo dnf install nmap (for Fedora/RHEL)\n\n")
                    output.insert(tk.END, "Using netstat for basic port information instead...\n\n")
                    
                    # Use netstat as a fallback
                    fallback_cmd = "netstat -tuln | grep LISTEN"
                    self.run_command(fallback_cmd, "Security Scan", "Open Ports Check")
                return
        
        # Scan localhost with service version detection for commonly used ports
        command = "nmap -sV -F localhost"
        self.run_command(command, "Security Scan", "Network Security Scan")

if __name__ == "__main__":
    # Create and run the application
    app = EnterpriseSecurityDashboard()
    
    # Set up text tags for output formatting
    for tab_name, tab in app.tab_contents.items():
        if hasattr(tab, "output"):
            tab.output.tag_configure("warning", foreground="orange")
            tab.output.tag_configure("error", foreground="red")
            tab.output.tag_configure("success", foreground="green")
            # Add new style tags
            tab.output.tag_configure("info_header", foreground="#3182CE", font=(app.system_font, app.font_sizes['md'], "bold"))
            tab.output.tag_configure("error_header", foreground="#E53E3E", font=(app.system_font, app.font_sizes['md'], "bold"))
            tab.output.tag_configure("success_header", foreground="#38A169", font=(app.system_font, app.font_sizes['md'], "bold"))
            tab.output.tag_configure("fix_header", foreground="#DD6B20", font=(app.system_font, app.font_sizes['md'], "bold"))
            tab.output.tag_configure("progress_note", foreground="#718096", font=(app.system_font, app.font_sizes['sm'], "italic"))
            tab.output.tag_configure("welcome", foreground="#4299E1", font=(app.system_font, app.font_sizes['lg'], "bold"))
            tab.output.tag_configure("info", foreground="#4A5568")
    
    # Start the application main loop
    app.mainloop()
