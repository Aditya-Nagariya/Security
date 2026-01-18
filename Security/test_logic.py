import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Ensure we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from system_detector import SystemDetector, CommandResult
from security_dashboard import ConfigManager, Scanner, Hardener

class TestSystemDetector(unittest.TestCase):
    def setUp(self):
        self.detector = SystemDetector(simulation_mode=True)

    def test_simulation_mode_active(self):
        self.assertTrue(self.detector.simulation_mode)

    def test_validate_command_simulation(self):
        # In simulation mode, everything should exist
        self.assertTrue(self.detector.validate_command("non_existent_command"))

    def test_run_command_simulation(self):
        result = self.detector.run_command(["echo", "hello"])
        self.assertEqual(result.return_code, 0)
        self.assertIn("[SIM]", result.stdout)

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        # Create a dummy config file
        with open("test_config.yaml", "w") as f:
            f.write("app:\n  name: TestApp\n")
        self.config = ConfigManager("test_config.yaml")

    def tearDown(self):
        if os.path.exists("test_config.yaml"):
            os.remove("test_config.yaml")

    def test_load_config(self):
        self.assertEqual(self.config.get("app.name"), "TestApp")

    def test_default_values(self):
        self.assertEqual(self.config.get("non.existent", "default"), "default")

class TestSecurityModules(unittest.TestCase):
    def setUp(self):
        self.detector = SystemDetector(simulation_mode=True)
        self.config = ConfigManager("non_existent.yaml") # Use defaults
        self.scanner = Scanner(self.detector, self.config)
        self.hardener = Hardener(self.detector, self.config)

    def test_scanner_lynis(self):
        result = self.scanner.run_lynis()
        self.assertIn("[SIM]", result)

    def test_hardener_ssh(self):
        result = self.hardener.harden_ssh()
        self.assertIn("SSH Hardened Successfully", result)

if __name__ == '__main__':
    unittest.main()
