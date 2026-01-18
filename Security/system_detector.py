"""
System Detector Module
----------------------
This module provides an abstraction layer for system operations, allowing for
cross-platform compatibility checks, simulation, and extensive logging.

It is designed to be safe to run on macOS for development purposes, with
simulation modes that mimic Linux behavior.
"""

import platform
import shutil
import subprocess
import logging
import os
import time
import shlex
from typing import List, Tuple, Optional, Union, Dict
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger("SystemDetector")

@dataclass
class CommandResult:
    """Standardized result from a system command execution."""
    return_code: int
    stdout: str
    stderr: str
    command: str
    duration: float

class SystemDetector:
    """
    Abstracts system interactions to support cross-distribution compatibility
    and safe simulation on non-Linux platforms.
    """
    
    def __init__(self, simulation_mode: bool = False, dry_run: bool = False):
        self.simulation_mode = simulation_mode
        self.dry_run = dry_run
        self.os_name = platform.system()
        self.distro = self._detect_distro()
        self.pkg_mgr = self._detect_pkg_mgr()
        self.is_linux = self.os_name == "Linux"
        
        # Warn if running on non-Linux without simulation
        if not self.is_linux and not self.simulation_mode:
            logger.warning(f"Running on {self.os_name} which is NOT Linux. Enabling simulation mode automatically for safety.")
            self.simulation_mode = True

        logger.info(f"System Initialized: OS={self.os_name}, Distro={self.distro}, PkgMgr={self.pkg_mgr}, Sim={self.simulation_mode}, DryRun={self.dry_run}")

    def _detect_distro(self) -> str:
        """
        Detects the specific Linux distribution.
        Returns 'macos', 'windows', or the linux distro ID (e.g., 'ubuntu', 'centos').
        """
        if self.os_name == "Linux":
            try:
                import distro
                return distro.id()
            except ImportError:
                # Fallback for systems without distro package
                try:
                    if os.path.exists("/etc/os-release"):
                        with open("/etc/os-release") as f:
                            for line in f:
                                if line.startswith("ID="):
                                    return line.split("=")[1].strip().strip('"')
                except Exception as e:
                    logger.error(f"Failed to detect distro via /etc/os-release: {e}")
                    return "unknown_linux"
        elif self.os_name == "Darwin":
            return "macos"
        elif self.os_name == "Windows":
            return "windows"
        return self.os_name.lower()

    def _detect_pkg_mgr(self) -> Optional[str]:
        """
        Detects the available package manager.
        """
        if self.simulation_mode:
            # In simulation, assume apt if on macOS/Windows acting as Ubuntu, or just return a default
            return "apt" 
            
        managers = ["apt", "dnf", "yum", "pacman", "zypper", "apk"]
        for mgr in managers:
            if shutil.which(mgr):
                logger.debug(f"Package manager detected: {mgr}")
                return mgr
        
        logger.warning("No supported package manager found.")
        return None

    def validate_command(self, command: str) -> bool:
        """
        Checks if a command exists in the system path.
        """
        if self.simulation_mode:
            return True
        exists = shutil.which(command) is not None
        if not exists:
            logger.warning(f"Command not found: {command}")
        return exists

    def validate_path(self, path: str, should_exist: bool = True) -> bool:
        """
        Checks if a path exists (or shouldn't exist).
        """
        if self.simulation_mode:
            return True
        
        exists = os.path.exists(path)
        if should_exist and not exists:
            logger.warning(f"Path expected but missing: {path}")
            return False
        if not should_exist and exists:
            logger.warning(f"Path exists but shouldn't: {path}")
            return False
        return True

    def run_command(self, command: Union[str, List[str]], timeout: int = 30, shell: bool = False, check: bool = False) -> CommandResult:
        """
        Executes a system command safely with timeout and logging.
        
        Args:
            command: The command string or list of arguments.
            timeout: Max time in seconds to wait.
            shell: Whether to use shell execution (AVOID if possible).
            check: Whether to raise exception on non-zero return code.
            
        Returns:
            CommandResult object containing output and status.
        """
        start_time = time.time()
        
        # Normalize command for logging and execution
        if isinstance(command, str) and not shell:
            # Split string command if not using shell=True
            cmd_list = shlex.split(command)
            cmd_str = command
        elif isinstance(command, list):
            cmd_list = command
            cmd_str = " ".join(command)
        else:
            cmd_list = command
            cmd_str = str(command)

        logger.debug(f"Preparing to execute: {cmd_str} (Timeout: {timeout}s, Shell: {shell})")

        # SIMULATION MODE
        if self.simulation_mode or self.dry_run:
            logger.info(f"[SIM/DRY] Would execute: {cmd_str}")
            time.sleep(0.1) # Tiny delay to simulate work
            return CommandResult(
                return_code=0,
                stdout=f"[SIM] Output for: {cmd_str}",
                stderr="",
                command=cmd_str,
                duration=0.1
            )

        # REAL EXECUTION
        try:
            # Security check: Validate command exists if it's the first arg
            if not shell and cmd_list and not self.validate_command(cmd_list[0]):
                raise FileNotFoundError(f"Command not found: {cmd_list[0]}")

            result = subprocess.run(
                command if shell else cmd_list,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            
            duration = time.time() - start_time
            logger.info(f"Command finished in {duration:.2f}s. Return Code: {result.returncode}")
            
            if result.returncode != 0:
                logger.error(f"Command failed: {cmd_str}\nStderr: {result.stderr}")
                if check:
                    raise subprocess.CalledProcessError(result.returncode, cmd_list, result.stdout, result.stderr)

            return CommandResult(
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                command=cmd_str,
                duration=duration
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            logger.error(f"Command timed out after {duration:.2f}s: {cmd_str}")
            return CommandResult(-1, "", "Command timed out", cmd_str, duration)
            
        except Exception as e:
            duration = time.time() - start_time
            logger.exception(f"Exception executing command: {cmd_str}")
            return CommandResult(-1, "", str(e), cmd_str, duration)

    def install_package(self, package: str) -> bool:
        """
        Installs a package using the detected package manager.
        """
        if not self.pkg_mgr:
            logger.error("Cannot install package: No package manager detected.")
            return False
            
        logger.info(f"Attempting to install package: {package}")
        
        cmds = {
            "apt": ["apt-get", "install", "-y", package],
            "dnf": ["dnf", "install", "-y", package],
            "yum": ["yum", "install", "-y", package],
            "pacman": ["pacman", "-S", "--noconfirm", package],
            "zypper": ["zypper", "install", "-y", package],
            "apk": ["apk", "add", package]
        }
        
        cmd = cmds.get(self.pkg_mgr)
        if not cmd:
            logger.error(f"No install command defined for {self.pkg_mgr}")
            return False
            
        # Use sudo if not root (simple check, can be improved)
        if os.geteuid() != 0 and not self.simulation_mode:
             # In a real scenario, we might need to handle sudo password or assume user has passwordless sudo
             # For this tool, we assume it's run with sufficient privileges or we prepend sudo
             cmd.insert(0, "sudo")

        result = self.run_command(cmd, timeout=300)
        return result.returncode == 0

    def backup_file(self, path: str) -> bool:
        """
        Creates a backup of a file with a timestamp.
        """
        if self.simulation_mode or self.dry_run:
            logger.info(f"[SIM] Would backup file: {path}")
            return True
            
        if not os.path.exists(path):
            logger.error(f"Cannot backup: File not found {path}")
            return False
            
        try:
            timestamp = int(time.time())
            backup_path = f"{path}.bak.{timestamp}"
            shutil.copy2(path, backup_path)
            logger.info(f"Backup created: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Backup failed for {path}: {e}")
            return False

    def check_service_status(self, service_name: str) -> str:
        """
        Checks the status of a system service.
        """
        if self.simulation_mode:
            return "active (running)"
            
        # Try systemctl first
        if self.validate_command("systemctl"):
            res = self.run_command(["systemctl", "is-active", service_name])
            return res.stdout.strip()
        
        # Fallback to service command
        if self.validate_command("service"):
            res = self.run_command(["service", service_name, "status"])
            return "active" if res.returncode == 0 else "inactive"
            
        return "unknown"
