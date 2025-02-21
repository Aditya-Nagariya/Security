#!/usr/bin/env python3

import os
import subprocess
import sys
import time
import shutil
import signal
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.theme import Theme
import psutil
import distro

# Custom theme for clean, minimal output
custom_theme = Theme({
    "info": "bold #00FFCC",
    "warning": "bold #FFCC00",
    "error": "bold #FF4444",
    "success": "bold #00FF00",
    "highlight": "bold #FF00FF",
    "progress": "#00FF00",
    "debug": "dim #AAAAAA"
})
console = Console(theme=custom_theme)

# Detect Linux distribution with fallback
def get_distribution():
    try:
        dist_id = distro.id()
        return dist_id.lower() if dist_id else "unknown"
    except Exception as e:
        console.print(f"[warning]Failed to detect distribution: {str(e) or 'Unknown'}. Using 'unknown'.[/warning]")
        return "unknown"

DISTRO = get_distribution()

# Package manager commands
PACKAGE_MANAGERS = {
    "ubuntu": {"update": "apt update && apt upgrade -y", "install": "apt install -y"},
    "debian": {"update": "apt update && apt upgrade -y", "install": "apt install -y"},
    "kali": {"update": "apt update && apt upgrade -y", "install": "apt install -y"},
    "fedora": {"update": "dnf update -y", "install": "dnf install -y"},
    "arch": {"update": "pacman -Syu --noconfirm", "install": "pacman -S --noconfirm"},
    "unknown": {"update": "apt update && apt upgrade -y", "install": "apt install -y"}  # Fallback
}

# Global state
RUNNING_PROCESSES = []
TEMP_FILES = []

# Detect terminal size with correct handling
def get_terminal_size():
    try:
        terminal_columns, terminal_rows = os.get_terminal_size()
    except Exception:
        try:
            terminal_columns, terminal_rows = shutil.get_terminal_size()
        except Exception:
            console.print("[error]Cannot detect terminal size. Ensure you're running in a terminal.[/error]")
            sys.exit(1)
    
    console.print(f"[debug]Detected terminal size: {terminal_rows} rows x {terminal_columns} columns[/debug]", highlight=False)
    
    if terminal_rows < 10 and terminal_columns > 1000:
        console.print("[debug]Correcting potential dimension swap[/debug]", highlight=False)
        terminal_rows, terminal_columns = terminal_columns, terminal_rows
    
    if terminal_rows < 20 or terminal_columns < 80:
        console.print(f"[error]Terminal too small: {terminal_rows} rows x {terminal_columns} columns. Minimum 20x80 required.[/error]")
        sys.exit(1)
    
    return terminal_rows, terminal_columns

# Check root privileges
def check_root():
    if os.getuid() != 0:
        console.print("[error]This script requires root privileges. Run with 'sudo'.[/error]")
        sys.exit(1)

# Get system stats with fallback
def get_system_stats():
    try:
        cpu = psutil.cpu_percent(interval=0.1) or 0.0
        memory = psutil.virtual_memory().percent or 0.0
        disk = psutil.disk_usage('/').percent or 0.0
        return cpu, memory, disk
    except Exception as e:
        console.print(f"[warning]Failed to get system stats: {str(e) or 'Unknown'}. Using defaults (0.0%).[/warning]")
        return 0.0, 0.0, 0.0

# Safe string formatting
def safe_format(value, default="Unknown"):
    try:
        if value is None:
            return str(default)
        return str(value)
    except Exception as e:
        console.print(f"[debug]Failed to format value: {str(e) or 'Unknown'}[/debug]", highlight=False)
        return str(default)

# Cleanup function
def cleanup(signum=None, frame=None):
    try:
        console.print("[warning]Cleaning up...[/warning]")
        for proc in RUNNING_PROCESSES[:]:
            if proc and hasattr(proc, 'poll') and proc.poll() is None:
                proc.terminate()
                time.sleep(0.1)
                if proc.poll() is None:
                    proc.kill()
        for temp_file in TEMP_FILES[:]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError as e:
                    console.print(f"[warning]Failed to remove {temp_file}: {safe_format(e, 'Unknown')}[/warning]")
        console.show_cursor(True)
        console.print("[success]Cleanup completed.[/success]")
    except Exception as e:
        console.print(f"[error]Cleanup error: {safe_format(str(e), 'Unknown')}[/error]")
    sys.exit(0 if signum is None else 1)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

# Install package
def install_package(package):
    pm_install = PACKAGE_MANAGERS.get(DISTRO, {"install": "apt install -y"})["install"]
    try:
        if shutil.which(package.split()[0]) is None:
            console.print(f"[info]Installing {package}...[/info]")
            proc = subprocess.Popen(f"{pm_install} {package}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            RUNNING_PROCESSES.append(proc)
            output, error = proc.communicate()
            if proc.returncode != 0:
                raise subprocess.CalledProcessError(proc.returncode, cmd=f"{pm_install} {package}", stderr=error or "Unknown")
            if proc in RUNNING_PROCESSES:
                RUNNING_PROCESSES.remove(proc)
            console.print(f"[success]Installed {package}[/success]")
    except subprocess.CalledProcessError as e:
        console.print(f"[error]Failed to install {package}: {safe_format(e.stderr, safe_format(e, 'Unknown'))}[/error]")
        raise
    except Exception as e:
        console.print(f"[error]Unexpected error installing {package}: {safe_format(str(e), 'Unknown')}[/error]")
        raise

# Run task with single-line progress and loading spinner
def run_task(description, command, estimated_duration=10, rollback_cmd=None):
    console.print(f"[info]Starting {description}. Press Ctrl+C to cancel.[/info]")
    try:
        proc = subprocess.Popen(f"{command} 2>&1", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        RUNNING_PROCESSES.append(proc)
        output_lines = []
        start_time = time.time()

        terminal_rows, _ = get_terminal_size()
        max_output_lines = max(1, (terminal_rows - 5) // 2)
        with console.status(f"[progress]{description}: 0%[/progress]", spinner="dots") as status:
            while proc.poll() is None:
                line = proc.stdout.readline()
                if line:
                    output_lines.append(line.strip())
                    if len(output_lines) > max_output_lines:
                        output_lines.pop(0)
                elapsed = time.time() - start_time
                percent = min(100, (elapsed / estimated_duration) * 100)
                status.update(f"[progress]{description}: {percent:.0f}%[/progress]")
                time.sleep(0.1)

        output, error = proc.communicate()
        if proc in RUNNING_PROCESSES:
            RUNNING_PROCESSES.remove(proc)

        if proc.returncode != 0:
            console.print(f"[error]Task failed: {safe_format(error, safe_format(output, 'Unknown'))}[/error]")
            if rollback_cmd:
                console.print("[warning]Rolling back...[/warning]")
                subprocess.run(rollback_cmd, shell=True, check=False)
            return False
        else:
            console.print("[success]Task completed![/success]")
            final_output = "\n".join(output_lines[-max_output_lines:]) if output_lines else "[dim]No output[/dim]"
            console.print(f"[yellow]Output:[/yellow]\n{final_output}")
            return True

    except KeyboardInterrupt:
        proc.terminate()
        time.sleep(0.1)
        if proc.poll() is None:
            proc.kill()
        console.print("[warning]Task cancelled.[/warning]")
        if proc in RUNNING_PROCESSES:
            RUNNING_PROCESSES.remove(proc)
        if rollback_cmd:
            console.print("[warning]Rolling back...[/warning]")
            subprocess.run(rollback_cmd, shell=True, check=False)
        return False

    except Exception as e:
        console.print(f"[error]Task error: {safe_format(str(e), 'Unknown')}[/error]")
        if 'proc' in locals() and proc in RUNNING_PROCESSES:
            RUNNING_PROCESSES.remove(proc)
        if rollback_cmd:
            console.print("[warning]Rolling back...[/warning]")
            subprocess.run(rollback_cmd, shell=True, check=False)
        return False

# Create dashboard with minimal rendering
def create_dashboard(selected_option=1):
    try:
        terminal_rows, terminal_columns = get_terminal_size()
        console.print("[bright_magenta]GOD-LEVEL SECURITY DASHBOARD[/bright_magenta]")

        options = [
            "Perform Security Scan", "Update System", "Clean System", "Malware Scan",
            "Security Hardening", "Network Security", "Backup System", "System Monitoring",
            "Log Analysis", "Secure SSH", "Pentest Tools", "Web Security",
            "Bandwidth Monitor", "Container Security", "Wireless Security", "Generate Report",
            "File Integrity Check", "Security Audit"
        ]
        max_menu_rows = min(18, max(1, (terminal_rows - 10) // 2))
        console.print("[cyan]Menu:[/cyan]")
        for i, option in enumerate(options[:max_menu_rows], 1):
            style = "highlight" if i == selected_option else "info"
            console.print(f"[{style}]{i}. {option}[/{style}]")
        if len(options) > max_menu_rows:
            console.print(f"[dim][more options: {max_menu_rows + 1}-18][/dim]")
        console.print(f"[debug]menu_table created with {len(options[:max_menu_rows])} rows[/debug]", highlight=False)

        console.print("[cyan]Output:[/cyan]")
        console.print("[dim]Awaiting output...[/dim]")

        cpu, memory, disk = get_system_stats()
        console.print("[green]System Status:[/green]")
        console.print(f"[green]CPU:     {cpu:.1f}%[/green]")
        console.print(f"[green]Memory:  {memory:.1f}%[/green]")
        console.print(f"[green]Disk:    {disk:.1f}%[/green]")
        console.print("[debug]status_table created successfully[/debug]", highlight=False)

    except Exception as e:
        console.print(f"[error]Dashboard creation error: {safe_format(str(e), 'Unknown')}[/error]")
        sys.exit(1)

# Interactive menu with static display
def interactive_menu():
    console.clear()
    console.show_cursor(False)
    selected = 1
    while True:
        try:
            create_dashboard(selected)
            console.print("[info]Navigate: ↑ (up), ↓ (down), Enter (select), Ctrl+C (exit)[/info]")
            choice = console.input("Choice (1-18): ").strip().lower()
            
            if choice == "":
                continue
            elif choice == "up":
                selected = max(1, selected - 1)
            elif choice == "down":
                selected = min(18, selected + 1)
            elif choice.isdigit() and 1 <= int(choice) <= 18:
                return int(choice)
            elif choice == "exit":
                return 0
            else:
                console.print("[error]Invalid input. Use ↑, ↓, Enter, or 1-18.[/error]")
        except KeyboardInterrupt:
            return 0
        except Exception as e:
            console.print(f"[error]Menu error: {safe_format(str(e), 'Unknown')}. Falling back to manual input.[/error]")
            return fallback_menu()

# Fallback menu
def fallback_menu():
    console.print("[info]Manual menu selection (type 0-18, 0 to exit):[/info]")
    options = [
        "0. Exit", "1. Perform Security Scan", "2. Update System", "3. Clean System", "4. Malware Scan",
        "5. Security Hardening", "6. Network Security", "7. Backup System", "8. System Monitoring",
        "9. Log Analysis", "10. Secure SSH", "11. Pentest Tools", "12. Web Security",
        "13. Bandwidth Monitor", "14. Container Security", "15. Wireless Security", "16. Generate Report",
        "17. File Integrity Check", "18. Security Audit"
    ]
    for opt in options:
        console.print(opt)
    while True:
        try:
            choice = int(Prompt.ask("[info]Enter choice: [/info]"))
            if 0 <= choice <= 18:
                return choice
            console.print("[error]Invalid choice. Select 0-18.[/error]")
        except ValueError:
            console.print("[error]Invalid input. Enter a number 0-18.[/error]")

# Security functions
def perform_security_scan():
    tools = [("lynis", "lynis audit system", 20), ("rkhunter", "rkhunter --check", 30), ("chkrootkit", "chkrootkit", 15)]
    for tool, cmd, duration in tools:
        try:
            install_package(tool)
            if not run_task(f"Scanning with {tool}...", cmd, duration):
                console.print("[warning]Scan interrupted.[/warning]")
                return
        except Exception as e:
            console.print(f"[error]Security scan error for {tool}: {safe_format(str(e), 'Unknown')}[/error]")
            return

def update_system():
    cmd = PACKAGE_MANAGERS.get(DISTRO, {"update": "apt update && apt upgrade -y"})["update"]
    if not run_task("Updating system...", cmd, 60):
        console.print("[warning]Update interrupted.[/warning]")

def clean_system():
    if Confirm.ask("[info]Clean system?[/info]"):
        if not run_task("Cleaning temp files...", "find /tmp -type f -delete", 5):
            return
        if DISTRO in ["ubuntu", "debian", "kali"]:
            if not run_task("Cleaning package cache...", "apt autoremove -y && apt autoclean", 10):
                return

def malware_scan():
    install_package("clamav")
    path = Prompt.ask("[info]Scan directory (default: /): [/info]", default="/")
    if not run_task("Scanning for malware...", f"clamscan -r {path}", 30):
        console.print("[warning]Scan interrupted.[/warning]")

def security_hardening():
    if DISTRO in ["ubuntu", "debian", "kali"]:
        install_package("ufw")
        if not run_task("Enabling firewall...", "ufw enable", 5):
            return
    if not run_task("Setting permissions...", "chmod -R go-rwx /root", 5):
        console.print("[warning]Hardening interrupted.[/warning]")

def network_security():
    if not run_task("Checking network...", "ss -tuln", 5):
        console.print("[warning]Network check interrupted.[/warning]")

def backup_system():
    src = Prompt.ask("[info]Backup directory (default: /home): [/info]", default="/home")
    dest = Prompt.ask("[info]Backup destination (default: /backup): [/info]", default="/backup")
    if not os.path.exists(dest):
        os.makedirs(dest)
    if not run_task("Creating backup...", f"tar -czf {dest}/backup-$(date +%F).tar.gz {src}", 20):
        console.print("[warning]Backup interrupted.[/warning]")

def system_monitoring():
    console.print("[info]Press Ctrl+C or 'q' to stop...[/info]")
    while True:
        try:
            cpu, memory, disk = get_system_stats()
            console.print("[green]System Monitoring:[/green]")
            console.print(f"[green]CPU:     {cpu:.1f}%[/green]")
            console.print(f"[green]Memory:  {memory:.1f}%[/green]")
            console.print(f"[green]Disk:    {disk:.1f}%[/green]")
            if console.input("[dim]Press 'q' to stop: [/dim]").lower() == 'q':
                break
            time.sleep(1)
        except KeyboardInterrupt:
            break

def log_analysis():
    install_package("logwatch")
    if not run_task("Analyzing logs...", "logwatch --detail High --service all", 10):
        console.print("[warning]Log analysis interrupted.[/warning]")

def secure_ssh():
    if Confirm.ask("[info]Secure SSH?[/info]"):
        backup = f"/etc/ssh/sshd_config.bak.{time.time()}"
        subprocess.run(f"cp /etc/ssh/sshd_config {backup}", shell=True, check=False)
        if not run_task("Securing SSH...", "sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && systemctl restart sshd", 5, rollback_cmd=f"mv {backup} /etc/ssh/sshd_config && systemctl restart sshd"):
            console.print("[warning]SSH hardening interrupted.[/warning]")

def pentest_tools():
    tools = {"nmap": "Network Scanner", "nikto": "Web Scanner", "sslscan": "SSL Scanner", "whatweb": "Web Fingerprinting"}
    console.print("[info]Tools:[/info]")
    for i, (tool, desc) in enumerate(tools.items(), 1):
        console.print(f"[{info}]{i}. {tool} - {desc}[/{info}]")
    choice = int(Prompt.ask("[info]Select tool (1-4): [/info]", choices=[str(i) for i in range(1, len(tools) + 1)]))
    install_package(list(tools.keys())[choice - 1])
    target = Prompt.ask("[info]Target (IP/domain): [/info]")
    if not run_task(f"Running {list(tools.keys())[choice - 1]}...", f"{list(tools.keys())[choice - 1]} {target}", 15):
        console.print("[warning]Pentest interrupted.[/warning]")

def web_security():
    if shutil.which("apache2") or shutil.which("nginx"):
        if not run_task("Securing web server...", "chmod 750 /var/www && chown -R www-data:www-data /var/www", 5):
            console.print("[warning]Web security interrupted.[/warning]")

def bandwidth_monitor():
    console.print("[info]Press Ctrl+C or 'q' to stop...[/info]")
    while True:
        try:
            net = psutil.net_io_counters()
            console.print("[green]Bandwidth Monitor:[/green]")
            console.print(f"[green]Sent:     {net.bytes_sent / 1024 / 1024:.2f} MB[/green]")
            console.print(f"[green]Received: {net.bytes_recv / 1024 / 1024:.2f} MB[/green]")
            if console.input("[dim]Press 'q' to stop: [/dim]").lower() == 'q':
                break
            time.sleep(1)
        except KeyboardInterrupt:
            break

def container_security():
    if shutil.which("docker"):
        install_package("docker-bench-security")
        if not run_task("Checking containers...", "docker-bench-security", 20):
            console.print("[warning]Container check interrupted.[/warning]")

def wireless_security():
    if shutil.which("iw"):
        if not run_task("Checking wireless...", "iw dev", 5):
            console.print("[warning]Wireless check interrupted.[/warning]")

def generate_report():
    report_file = f"security_report_{time.strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, "w") as f:
        f.write(f"Security Report\nDistribution: {DISTRO}\nDate: {time.ctime()}\n")
    if not run_task("Generating report...", f"cat {report_file}", 5):
        console.print("[warning]Report interrupted.[/warning]")
    console.print(f"[success]Report saved to {report_file}[/success]")

def file_integrity_check():
    install_package("aide-common")
    if not os.path.exists("/var/lib/aide/aide.db.gz"):
        if not run_task("Initializing AIDE...", "aide --init && mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz", 10):
            return
    if not run_task("Checking integrity...", "aide --check", 15):
        console.print("[warning]Integrity check interrupted.[/warning]")

def security_audit():
    install_package("tiger")
    if not run_task("Running audit...", "tiger", 20):
        console.print("[warning]Audit interrupted.[/warning]")

# Main loop
def main():
    try:
        check_root()
        console.show_cursor(False)
        FUNCTIONS = {
            1: perform_security_scan, 2: update_system, 3: clean_system, 4: malware_scan,
            5: security_hardening, 6: network_security, 7: backup_system, 8: system_monitoring,
            9: log_analysis, 10: secure_ssh, 11: pentest_tools, 12: web_security,
            13: bandwidth_monitor, 14: container_security, 15: wireless_security, 16: generate_report,
            17: file_integrity_check, 18: security_audit
        }
        while True:
            try:
                choice = interactive_menu()
                if choice == 0:
                    cleanup()
                    break
                elif choice in FUNCTIONS:
                    FUNCTIONS[choice]()
                    Prompt.ask("[info]Press Enter to continue...[/info]")
                else:
                    console.print("[error]Invalid choice. Select 0-18.[/error]")
                    time.sleep(1)
            except Exception as e:
                console.print(f"[error]Main loop error: {safe_format(str(e), 'Unknown')}. Continuing...[/error]")
                time.sleep(1)
    except Exception as e:
        console.print(f"[error]Critical error: {safe_format(str(e), 'Unknown')}. Cleaning up...[/error]")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
