from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class BuildSystemBase(ABC):
    """Abstract base class for all build systems."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the build system with configuration.

        Args:
            config: Dictionary containing build system configuration
        """
        self.config = config

    @abstractmethod
    def build(self, testbench: str, options: Optional[Dict[str, Any]] = None) -> bool:
        """Build the testbench.

        Args:
            testbench: Name of the testbench to build
            options: Additional build options

        Returns:
            bool: True if build was successful, False otherwise
        """
        pass

    @abstractmethod
    def run(self, testbench: str, test: str, options: Optional[Dict[str, Any]] = None) -> bool:
        """Run a specific test for the given testbench.

        Args:
            testbench: Name of the testbench
            test: Name of the test to run
            options: Additional run options

        Returns:
            bool: True if test run was successful, False otherwise
        """
        pass

    @abstractmethod
    def clean(self, testbench: str) -> bool:
        """Clean the testbench.

        Args:
            testbench: Name of the testbench to clean

        Returns:
            bool: True if clean was successful, False otherwise
        """
        pass

    @abstractmethod
    def get_available_testbenches(self) -> List[str]:
        """Get a list of available testbenches.

        Returns:
            List[str]: List of testbench names
        """
        pass

    @abstractmethod
    def get_available_tests(self, testbench: str) -> List[str]:
        """Get a list of available tests for a testbench.

        Args:
            testbench: Name of the testbench

        Returns:
            List[str]: List of test names
        """
        pass 