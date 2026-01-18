import subprocess
import platform
import logging
import shlex
import shutil
import os
from typing import List, Tuple, Union, Optional
from dataclasses import dataclass
import time

# Configure logging
logger = logging.getLogger("Aegis.System")

@dataclass
class CommandResult:
    return_code: int
    stdout: str
    stderr: str
    command: str
    duration: float

class SystemInterface:
    """
    Secure wrapper for system operations. 
    Handles command execution, simulation mode, and safety checks.
    """
    
    def __init__(self, simulation_mode: str = "auto"):
        self.os_type = platform.system()
        self._set_simulation_mode(simulation_mode)
        self.sudo_prefix = self._detect_sudo()
        
    def _set_simulation_mode(self, mode: str):
        if mode == "auto":
            # Simulate if not Linux
            self.simulation_mode = self.os_type != "Linux"
        elif mode == "true":
            self.simulation_mode = True
        else:
            self.simulation_mode = False
            
        if self.simulation_mode:
            logger.info(f"SystemInterface initialized in SIMULATION mode ({self.os_type})")
        else:
            logger.info("SystemInterface initialized in ACTIVE mode")

    def _detect_sudo(self) -> List[str]:
        if self.simulation_mode:
            return ["sudo"]
        
        # Check if we are already root
        if os.geteuid() == 0:
            return []
        
        # Check if sudo is available
        if shutil.which("sudo"):
            return ["sudo", "-S"] # -S reads password from stdin, useful for GUI
        
        return []

    def validate_command(self, cmd: str) -> bool:
        """Check if a command exists in the system path."""
        if self.simulation_mode:
            return True # Assume all tools exist in sim mode
        return shutil.which(cmd) is not None

    def run_command(self, command: Union[str, List[str]], require_sudo: bool = False, timeout: int = 30) -> CommandResult:
        """
        Execute a command safely.
        
        Args:
            command: Command string or list. Strings are safely split using shlex.
            require_sudo: Whether to prepend sudo.
            timeout: Execution timeout in seconds.
        """
        start_time = time.time()
        
        # Normalize command to list
        if isinstance(command, str):
            cmd_list = shlex.split(command)
        else:
            cmd_list = command
            
        # Add sudo if needed
        if require_sudo and self.sudo_prefix:
            # Avoid double sudo
            if cmd_list[0] != "sudo":
                cmd_list = self.sudo_prefix + cmd_list

        cmd_str = " ".join(cmd_list)
        
        # SIMULATION PATH
        if self.simulation_mode:
            time.sleep(0.5) # Fake latency
            logger.info(f"[SIM] Executing: {cmd_str}")
            return CommandResult(
                return_code=0,
                stdout=f"[SIMULATION OUTPUT] Successfully executed: {cmd_str}",
                stderr="",
                command=cmd_str,
                duration=time.time() - start_time
            )

        # REAL EXECUTION PATH
        try:
            logger.debug(f"Executing: {cmd_str}")
            
            # Security: shell=False is the default and enforced here by passing a list
            result = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            
            duration = time.time() - start_time
            return CommandResult(
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                command=cmd_str,
                duration=duration
            )
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {cmd_str}")
            return CommandResult(124, "", "Command timed out", cmd_str, time.time() - start_time)
        except FileNotFoundError:
            logger.error(f"Command not found: {cmd_list[0]}")
            return CommandResult(127, "", f"Command not found: {cmd_list[0]}", cmd_str, time.time() - start_time)
        except Exception as e:
            logger.exception(f"Unexpected error executing {cmd_str}")
            return CommandResult(1, "", str(e), cmd_str, time.time() - start_time)
