use async_trait::async_trait;
use crate::core::traits::SystemInterface;
use crate::core::types::{CommandResult, SecurityScanResult};
use chrono::Local;
use std::time::Duration;
use tokio::time::sleep;

#[derive(Default)]
pub struct MockSystem;

#[async_trait]
impl SystemInterface for MockSystem {
    fn check_tool_installed(&self, _tool_name: &str) -> bool {
        // In simulation, we pretend everything is installed
        true
    }

    async fn run_command(&self, command: &str, args: &[
&str], require_sudo: bool) -> CommandResult {
        // Simulate processing time
        sleep(Duration::from_millis(800)).await;
        
        let cmd_str = format!("{} {}", command, args.join(" "));
        let prefix = if require_sudo { "[SUDO] " } else { "" };
        
        CommandResult {
            success: true,
            stdout: format!("{}Simulated execution of: {}", prefix, cmd_str),
            stderr: String::new(),
        }
    }

    async fn run_security_scan(&self, scan_type: &str) -> SecurityScanResult {
        sleep(Duration::from_secs(2)).await;
        
        SecurityScanResult {
            timestamp: Local::now().format("%Y-%m-%d %H:%M:%S").to_string(),
            scan_type: scan_type.to_string(),
            score: 85,
            issues_found: vec![
                "WARNING: SSH Password Auth enabled (Simulated)".to_string(),
                "SUGGESTION: Install fail2ban (Simulated)".to_string()
            ],
            raw_output: "--- MOCK LYNIS REPORT ---
[+] System looks mostly secure
[!] Found 2 potential issues...".to_string(),
        }
    }
}
