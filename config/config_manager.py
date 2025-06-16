# No import changes needed - imports are standard library

import os
from typing import Any, Dict, Optional

import yaml


class ConfigManager:
    """Configuration management for the testing tool."""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize the configuration manager.

        Args:
            config_file: Path to the configuration file (YAML)
        """
        self.config_file = config_file or os.path.join(os.getcwd(), "config.yml")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load the configuration from file.

        Returns:
            Dict[str, Any]: The loaded configuration
        """
        if not os.path.exists(self.config_file):
            return {}

        try:
            with open(self.config_file, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading config file {self.config_file}: {e}")
            return {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key is not found

        Returns:
            Any: The configuration value or default
        """
        return self.config.get(key, default)

    def get_testbench_config(self, testbench: str) -> Dict[str, Any]:
        """Get configuration for a specific testbench.

        Args:
            testbench: Name of the testbench

        Returns:
            Dict[str, Any]: Testbench configuration
        """
        testbenches = self.config.get("testbenches", {})
        return testbenches.get(testbench, {})

    def get_test_config(self, testbench: str, test: str) -> Dict[str, Any]:
        """Get configuration for a specific test.

        Args:
            testbench: Name of the testbench
            test: Name of the test

        Returns:
            Dict[str, Any]: Test configuration
        """
        tb_config = self.get_testbench_config(testbench)
        tests = tb_config.get("tests", {})
        return tests.get(test, {})
