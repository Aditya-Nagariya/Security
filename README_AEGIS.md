# Project Aegis: Enterprise Security Dashboard (v3.0)

A complete modernization of the legacy security dashboard, featuring a professional UI, safe architecture, and real-time metrics.

## 🚀 Key Features
- **Modern UI**: Built with `customtkinter` for a native, dark-mode experience.
- **Safe Core**: Wraps all shell commands to prevent injection attacks and handling errors gracefully.
- **Simulation Mode**: Automatically mocks dangerous commands on non-Linux systems (macOS/Windows) for safe development.
- **Real-Time Metrics**: Uses `psutil` for sub-second accurate CPU/RAM/Disk monitoring.

## 🛠️ Installation

1. **Create a Virtual Environment** (Recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r Aegis/requirements.txt
   ```

## 🎮 Usage

### Run the GUI Dashboard
```bash
python3 main.py
```

### Run the Core Logic Verifier (CLI)
```bash
python3 Aegis/main_cli.py
```

## 📂 Structure
- `Aegis/src/ui/`: All GUI code (Windows, Widgets).
- `Aegis/src/core/`: Business logic (System Interface, Metrics).
- `Aegis/src/utils/`: Helper utilities.
- `Aegis/assets/`: Images and resources.

## 🛡️ Safety Note
This dashboard is designed to run with `sudo` privileges for certain actions (like updates or hardening). The `SystemInterface` handles this securely.
