# Development Guide

## Overview

This project is designed to be developed on macOS/Windows but deployed on Linux. To achieve this, we use a robust simulation and abstraction layer.

## Testing on macOS (No Linux VM required)

Since the developer cannot test on Linux directly, we rely on:
1.  **Simulation Mode**: Mocks all system calls.
2.  **Unit Tests**: Validates logic without executing commands.
3.  **Defensive Programming**: Extensive checks and logging.

### Running in Simulation Mode

To run the dashboard on macOS without triggering errors:

```bash
python3 security_dashboard.py --simulate
```

This will:
- Mock all `subprocess` calls.
- Pretend to be a Linux system (e.g., Ubuntu).
- Log what *would* have happened to the console/UI.

### Running Unit Tests

Run the test suite to verify logic:

```bash
python3 test_logic.py
```

### Key Components

- **`system_detector.py`**: The most critical file. It abstracts all OS interactions.
    - `run_command()`: Handles execution, timeouts, and simulation.
    - `validate_command()`: Checks if tools exist.
    - `install_package()`: Handles package managers.

- **`config.yaml`**: Centralized configuration. Do not hardcode paths in python files.

## Contribution Guidelines

1.  **Never use `shell=True`** unless absolutely necessary and safe.
2.  **Always use `SystemDetector`** methods, never `subprocess` or `os.system` directly.
3.  **Add Logging**: Log every major action using `self.logger`.
4.  **Update Tests**: If you add a new feature, add a test case in `test_logic.py`.

## Linux Validation (For Testers)

If you have access to a Linux machine, please verify:
- [ ] Package installation (apt/dnf/pacman) works.
- [ ] Service restarting (systemctl) works.
- [ ] File backups are created correctly.
- [ ] GUI is responsive during long scans.
