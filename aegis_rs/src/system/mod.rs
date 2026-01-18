pub mod mock;
pub mod linux;

pub use mock::MockSystem;
pub use linux::LinuxSystem;

// Factory to get the correct system based on compile target or config
#[cfg(target_os = "linux")]
pub type DefaultSystem = LinuxSystem;

#[cfg(not(target_os = "linux"))]
pub type DefaultSystem = MockSystem;
