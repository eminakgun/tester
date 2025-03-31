from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class SimulatorBase(ABC):
    """Abstract base class for all simulators."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the simulator with configuration.

        Args:
            config: Dictionary containing simulator configuration
        """
        self.config = config

    @abstractmethod
    def compile(self, testbench: str, options: Optional[Dict[str, Any]] = None) -> bool:
        """Compile the testbench.

        Args:
            testbench: Name of the testbench to compile
            options: Additional compile options

        Returns:
            bool: True if compilation was successful, False otherwise
        """
        pass

    @abstractmethod
    def simulate(self, testbench: str, test: str, options: Optional[Dict[str, Any]] = None) -> bool:
        """Run simulation for a specific test.

        Args:
            testbench: Name of the testbench
            test: Name of the test to run
            options: Additional simulation options

        Returns:
            bool: True if simulation was successful, False otherwise
        """
        pass

    @abstractmethod
    def clean(self, testbench: str) -> bool:
        """Clean the testbench simulation artifacts.

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