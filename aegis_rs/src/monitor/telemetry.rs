use sysinfo::{CpuRefreshKind, RefreshKind, System};
use crate::core::types::SystemMetrics;

pub struct TelemetryCollector {
    sys: System,
}

impl TelemetryCollector {
    pub fn new() -> Self {
        Self {
            sys: System::new_with_specifics(
                RefreshKind::new().with_cpu(CpuRefreshKind::everything())
            ),
        }
    }

    pub fn collect(&mut self) -> SystemMetrics {
        self.sys.refresh_all();
        
        let cpu_usage = self.sys.global_cpu_info().cpu_usage();
        let total_mem = self.sys.total_memory() as f32;
        let used_mem = self.sys.used_memory() as f32;
        let memory_usage = if total_mem > 0.0 { (used_mem / total_mem) * 100.0 } else { 0.0 };
        
        // Simple disk usage stub (sysinfo requires looping through disks)
        let disk_usage = 45.0; // Placeholder

        SystemMetrics {
            cpu_usage,
            memory_usage,
            disk_usage,
            uptime_seconds: System::uptime(),
        }
    }
}
