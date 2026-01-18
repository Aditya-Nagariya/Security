# Aegis Security Dashboard - Architecture Plan

## 1. UI Layer (src/ui)
- **Framework**: CustomTkinter (Modern, Dark Mode native)
- **Components**:
  - `DashboardWindow`: Main container with sidebar navigation
  - `MetricCard`: Reusable widget for CPU/RAM/Network stats
  - `ConsoleWidget`: Real-time log streaming with ANSI color support
  - `ActionPanel`: Grouped security operations (Scan, Harden, Monitor)

## 2. Core Logic (src/core)
- **`SecurityEngine`**: Facade for all security operations.
- **`SystemIntervention`**: Safe wrapper for `subprocess`.
  - Enforces `shell=False`
  - Handles `sudo` prompts via GUI callbacks (future)
  - Simulation mode for non-Linux dev environments

## 3. Data Layer
- **`MetricStream`**: Async/Threaded poller using `psutil`.
- **`AuditLogger`**: Structured JSON logging for compliance.

## 4. Safety Features
- **Simulation Mode**: Auto-detects macOS/Windows and mocks Linux commands.
- **Dry Run**: Preview commands before execution.
