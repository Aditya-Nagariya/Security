use std::process::Command;
use std::time::Instant;
use anyhow::{Result, anyhow};
use std::env;

#[derive(Debug, Clone)]
pub struct CommandResult {
    pub success: bool,
    pub stdout: String,
    pub stderr: String,
    pub duration: f64,
}

pub struct SystemDetector {
    pub simulation_mode: bool,
    pub os_type: String,
}

impl SystemDetector {
    pub fn new() -> Self {
        let os_type = env::consts::OS.to_string();
        // Auto-enable simulation on non-Linux unless overridden (logic similar to Python)
        let simulation_mode = os_type != "linux";
        
        Self {
            simulation_mode,
            os_type,
        }
    }

    pub fn run_command(&self, cmd: &str, args: &[&str]) -> CommandResult {
        let start = Instant::now();

        if self.simulation_mode {
            // Simulation Mode logic
            std::thread::sleep(std::time::Duration::from_millis(500)); // Fake latency
            return CommandResult {
                success: true,
                stdout: format!("[SIMULATION] Executed: {} {}\nSuccess.", cmd, args.join(" ")),
                stderr: String::new(),
                duration: start.elapsed().as_secs_f64(),
            };
        }

        // Real Execution
        match Command::new(cmd).args(args).output() {
            Ok(output) => CommandResult {
                success: output.status.success(),
                stdout: String::from_utf8_lossy(&output.stdout).to_string(),
                stderr: String::from_utf8_lossy(&output.stderr).to_string(),
                duration: start.elapsed().as_secs_f64(),
            },
            Err(e) => CommandResult {
                success: false,
                stdout: String::new(),
                stderr: format!("Failed to execute command: {}", e),
                duration: start.elapsed().as_secs_f64(),
            },
        }
    }

    // --- Security Operations ---

    pub fn scan_lynis(&self) -> CommandResult {
        self.run_command("lynis", &["audit", "system", "--quick", "--no-colors"])
    }

    pub fn scan_clamav(&self) -> CommandResult {
        self.run_command("clamscan", &["-r", "/tmp", "--no-summary"])
    }

    pub fn harden_ssh(&self) -> CommandResult {
        // In a real impl, this would edit /etc/ssh/sshd_config
        // For this prototype, we'll simulate the critical logic or use sed if on Linux
        if self.simulation_mode {
            return self.run_command("sed", &["-i", "s/PermitRootLogin yes/PermitRootLogin no/", "/fake/path/sshd_config"]);
        }
        
        // Safety: Refuse to actually break SSH on dev machine without sudo/linux checks
        // We defer to the run_command's logic which will fail if not root/linux
        self.run_command("sed", &["-i", "s/^PermitRootLogin.*/PermitRootLogin no/", "/etc/ssh/sshd_config"])
    }

    pub fn enable_firewall(&self) -> CommandResult {
        if self.simulation_mode {
            return self.run_command("ufw", &["enable"]);
        }
        self.run_command("ufw", &["--force", "enable"])
    }
}
