use async_trait::async_trait;
use crate::core::traits::SystemInterface;
use crate::core::types::{CommandResult, SecurityScanResult};
use chrono::Local;
use tokio::process::Command;

#[derive(Default)]
pub struct LinuxSystem;

#[async_trait]
impl SystemInterface for LinuxSystem {
    fn check_tool_installed(&self, tool_name: &str) -> bool {
        which::which(tool_name).is_ok()
    }

    async fn run_command(&self, command: &str, args: &[&str], _require_sudo: bool) -> CommandResult {
        // Note: Real sudo handling would require pkexec or similar in a GUI context
        let output = Command::new(command)
            .args(args)
            .output()
            .await;

        match output {
            Ok(out) => CommandResult {
                success: out.status.success(),
                stdout: String::from_utf8_lossy(&out.stdout).to_string(),
                stderr: String::from_utf8_lossy(&out.stderr).to_string(),
            },
            Err(e) => CommandResult {
                success: false,
                stdout: String::new(),
                stderr: e.to_string(),
            }
        }
    }

    async fn run_security_scan(&self, scan_type: &str) -> SecurityScanResult {
        if !self.check_tool_installed("lynis") {
             return SecurityScanResult {
                timestamp: Local::now().format("%Y-%m-%d %H:%M:%S").to_string(),
                scan_type: scan_type.to_string(),
                score: 0,
                issues_found: vec!["Error: Lynis is not installed.".to_string()],
                raw_output: "Please install lynis: sudo apt install lynis".to_string(),
            };
        }

        // Run Lynis (Note: This will likely need sudo in production)
        // We use --quick and --no-colors for parsing simplicity
        let result = self.run_command("lynis", &["audit", "system", "--quick", "--no-colors"], true).await;

        SecurityScanResult {
            timestamp: Local::now().format("%Y-%m-%d %H:%M:%S").to_string(),
            scan_type: scan_type.to_string(),
            score: if result.success { 100 } else { 0 }, // Placeholder scoring logic
            issues_found: if result.success { vec!["Scan Completed".to_string()] } else { vec!["Scan Failed".to_string()] },
            raw_output: if result.success { result.stdout } else { result.stderr },
        }
    }
}
