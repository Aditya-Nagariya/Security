# Installation Guide

## Prerequisites

- **Operating System**: Linux (Ubuntu, Debian, CentOS, RHEL, Fedora, Arch, Alpine)
- **Python**: Version 3.7 or higher
- **Root Privileges**: Required for most security operations

## Installation Steps

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/security-dashboard.git
    cd security-dashboard
    ```

2.  **Install System Dependencies**
    
    *Debian/Ubuntu:*
    ```bash
    sudo apt update
    sudo apt install python3-tk python3-pip ufw clamav lynis
    ```

    *RHEL/CentOS/Fedora:*
    ```bash
    sudo dnf install python3-tkinter python3-pip ufw clamav lynis
    ```

    *Arch Linux:*
    ```bash
    sudo pacman -S python-tk python-pip ufw clamav lynis
    ```

3.  **Install Python Dependencies**
    ```bash
    pip3 install -r requirements.txt
    ```

## Configuration

Edit `config.yaml` to customize the dashboard behavior:

```yaml
security:
  allowed_ports: [22, 80, 443]
  critical_services: ["sshd", "ufw"]
```

## Running the Application

**GUI Mode:**
```bash
sudo python3 security_dashboard.py
```

**Simulation Mode (Safe for testing):**
```bash
python3 security_dashboard.py --simulate
```

**Debug Mode:**
```bash
sudo python3 security_dashboard.py --debug
```

## Troubleshooting

- **"ImportError: No module named yaml"**: Run `pip3 install PyYAML`.
- **"Permission denied"**: Ensure you are running with `sudo`.
- **"Display not found"**: If running over SSH, ensure X11 forwarding is enabled (`ssh -X user@host`).
