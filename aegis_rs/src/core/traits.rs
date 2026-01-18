use async_trait::async_trait;
use crate::core::types::{CommandResult, SecurityScanResult};

#[async_trait]
pub trait SystemInterface: Send + Sync {
    /// Checks if a specific tool (e.g., "lynis", "ufw") is installed.
    fn check_tool_installed(&self, tool_name: &str) -> bool;

    /// Executes a shell command and returns the result.
    async fn run_command(&self, command: &str, args: &[&str], require_sudo: bool) -> CommandResult;

    /// Runs a specific security scan.
    async fn run_security_scan(&self, scan_type: &str) -> SecurityScanResult;
}
