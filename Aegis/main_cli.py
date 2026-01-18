import sys
import os
import time
import logging

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.system_interface import SystemInterface
from src.core.metrics import SystemMetrics

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Aegis.CLI")

def main():
    print("🛡️  Aegis Security System - Core Logic Verification")
    print("------------------------------------------------")
    
    # 1. Initialize System Interface
    sys_int = SystemInterface(simulation_mode="auto")
    print(f"[*] System Interface: {'SIMULATION' if sys_int.simulation_mode else 'ACTIVE'} Mode")
    
    # 2. Check Static Info
    info = SystemMetrics.get_static_info()
    print(f"[*] Host: {info['node']} ({info['system']} {info['release']})")
    
    # 3. Test Command Execution (Safe Wrapper)
    print("\n[*] Testing Safe Command Wrapper...")
    
    # Test 1: Simple list command
    cmd1 = ["ls", "-la"]
    print(f"    > Running: {' '.join(cmd1)}")
    res1 = sys_int.run_command(cmd1)
    print(f"    > Result Code: {res1.return_code}")
    print(f"    > Output Preview: {res1.stdout[:50]}...")
    
    # Test 2: Sudo command (Simulated on macOS/Windows, Real on Linux)
    cmd2 = ["apt", "update"]
    print(f"    > Running (Root): {' '.join(cmd2)}")
    res2 = sys_int.run_command(cmd2, require_sudo=True)
    print(f"    > Result Code: {res2.return_code}")
    print(f"    > Output: {res2.stdout.strip()}")

    # 4. Test Real-time Metrics
    print("\n[*] Testing Metrics Collection (5 samples)...")
    try:
        for i in range(5):
            metrics = SystemMetrics.get_realtime_metrics()
            print(f"    [{i+1}/5] CPU: {metrics['cpu']['usage']}% | "
                  f"RAM: {metrics['memory']['percent']}% | "
                  f"Disk: {metrics['disk']['percent']}% ")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")

    print("\n✅ Core Logic Verification Complete.")

if __name__ == "__main__":
    main()
