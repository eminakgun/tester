import os
import logging
import shutil
from typing import Dict, List, Optional, Any
import edalize
from pathlib import Path
import importlib

from build_systems.base import BuildSystemBase

logger = logging.getLogger(__name__)


class EdalizeIntegration(BuildSystemBase):
    """Build system implementation that uses Edalize for EDA tool interactions."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the Edalize integration with configuration.

        Args:
            config: Dictionary containing build system configuration
        """
        super().__init__(config)
        self.work_root = config.get("work_root", os.path.join(os.getcwd(), "build"))
        self.tool = config.get("tool", "icarus")  # Default to Icarus for testing
        self.parameters = config.get("parameters", {})
        self.files = config.get("files", [])
        self.testbenches = config.get("testbenches", {})
        
        # Set up tool-specific configurations
        self.tool_options = {
            "vcs": config.get("vcs_options", {}),
            "questa": config.get("questa_options", {}),
            "xcelium": config.get("xcelium_options", {})
        }

    def _prepare_edalize_config(self, testbench: str, test: Optional[str] = None) -> Dict[str, Any]:
        """Prepare the Edalize configuration for a testbench.

        Args:
            testbench: Name of the testbench
            test: Optional test name

        Returns:
            Dict[str, Any]: Edalize configuration
        """
        # Start with base configuration
        edam = {
            "name": testbench,
            "files": self.files.copy(),
            "parameters": self.parameters.copy(),
            "toplevel": self.testbenches.get(testbench, {}).get("toplevel", testbench)
        }
        
        # Add testbench-specific files
        tb_files = self.testbenches.get(testbench, {}).get("files", [])
        edam["files"].extend(tb_files)
        
        # Add testbench-specific parameters
        tb_params = self.testbenches.get(testbench, {}).get("parameters", {})
        edam["parameters"].update(tb_params)
        
        # Add test-specific parameters if test is provided
        if test:
            test_params = self.testbenches.get(testbench, {}).get("tests", {}).get(test, {})
            if test_params:
                # Special handling for UVM test name
                if "uvm_testname" not in test_params and self.tool in ["vcs", "questa", "xcelium"]:
                    test_params["uvm_testname"] = test
                
                edam["parameters"].update(test_params)
        
        # Add tool-specific options
        edam["tool_options"] = {
            self.tool: self.tool_options.get(self.tool, {})
        }
        
        return edam

    def _get_edalize_backend(self, testbench: str, test: Optional[str] = None) -> Any:
        """Get an Edalize backend for the specified testbench and test.

        Args:
            testbench: Name of the testbench
            test: Optional test name

        Returns:
            Any: Configured Edalize backend
        """
        edam = self._prepare_edalize_config(testbench, test)
        
        # Create work directory
        work_dir = os.path.join(self.work_root, testbench)
        os.makedirs(work_dir, exist_ok=True)
        
        # Create backend using updated edalize API
        try:
            # The newer edalize API
            if hasattr(edalize, 'get_edam_tool'):
                backend = edalize.get_edam_tool(self.tool, edam, work_dir)
            # Fallback to direct import
            else:
                # Try dynamic import
                tool_module = importlib.import_module(f"edalize.{self.tool}")
                tool_class = getattr(tool_module, self.tool.capitalize())
                backend = tool_class(edam=edam, work_root=work_dir)
            
            return backend
        except Exception as e:
            logger.error(f"Failed to create Edalize backend: {e}")
            raise

    def build(self, testbench: str, options: Optional[Dict[str, Any]] = None) -> bool:
        """Build the testbench using Edalize.

        Args:
            testbench: Name of the testbench to build
            options: Additional build options

        Returns:
            bool: True if build was successful, False otherwise
        """
        try:
            backend = self._get_edalize_backend(testbench)
            
            # Handle debug mode
            if options and options.get("debug"):
                if self.tool == "vcs":
                    backend.tool_options["vcs"]["debug"] = True
                elif self.tool == "questa":
                    backend.tool_options["questa"]["vopt_args"] = "-debug"
                elif self.tool == "xcelium":
                    backend.tool_options["xcelium"]["xrun_args"] = "-debug"
            
            # Clean build if requested
            if options and not options.get("incremental", True):
                logger.info(f"Performing clean build for testbench {testbench}")
                self.clean(testbench)
            
            # Configure and build
            logger.info(f"Configuring testbench {testbench} with {self.tool}")
            backend.configure()
            
            logger.info(f"Building testbench {testbench} with {self.tool}")
            backend.build()
            
            return True
        except Exception as e:
            logger.error(f"Failed to build testbench {testbench}: {e}")
            return False

    def run(self, testbench: str, test: str, options: Optional[Dict[str, Any]] = None) -> bool:
        """Run a specific test for the given testbench using Edalize.

        Args:
            testbench: Name of the testbench
            test: Name of the test to run
            options: Additional run options

        Returns:
            bool: True if test run was successful, False otherwise
        """
        try:
            backend = self._get_edalize_backend(testbench, test)
            
            # Handle run options
            run_options = {}
            
            # Handle seed
            if options and "seed" in options:
                if self.tool == "vcs":
                    run_options["ntb_random_seed"] = str(options["seed"])
                elif self.tool == "questa":
                    run_options["sv_seed"] = str(options["seed"])
                elif self.tool == "xcelium":
                    run_options["seed"] = str(options["seed"])
            
            # Handle verbosity
            if options and "verbosity" in options:
                verbosity = options["verbosity"].upper()
                if not verbosity.startswith("UVM_"):
                    verbosity = f"UVM_{verbosity}"
                run_options["UVM_VERBOSITY"] = verbosity
            
            # Configure if needed
            if not os.path.exists(os.path.join(self.work_root, testbench, "Makefile")):
                logger.info(f"Configuring testbench {testbench} with {self.tool}")
                backend.configure()
            
            # Run the test
            logger.info(f"Running test {test} for testbench {testbench} with {self.tool}")
            backend.run(run_options)
            
            return True
        except Exception as e:
            logger.error(f"Failed to run test {test} for testbench {testbench}: {e}")
            return False

    def clean(self, testbench: str) -> bool:
        """Clean the testbench build artifacts.

        Args:
            testbench: Name of the testbench to clean

        Returns:
            bool: True if clean was successful, False otherwise
        """
        work_dir = os.path.join(self.work_root, testbench)
        
        try:
            if os.path.exists(work_dir):
                logger.info(f"Cleaning directory {work_dir}")
                shutil.rmtree(work_dir)
            return True
        except Exception as e:
            logger.error(f"Failed to clean testbench {testbench}: {e}")
            return False

    def get_available_testbenches(self) -> List[str]:
        """Get a list of available testbenches from configuration.

        Returns:
            List[str]: List of testbench names
        """
        return list(self.testbenches.keys())

    def get_available_tests(self, testbench: str) -> List[str]:
        """Get a list of available tests for a testbench from configuration.

        Args:
            testbench: Name of the testbench

        Returns:
            List[str]: List of test names
        """
        if testbench not in self.testbenches:
            logger.warning(f"Unknown testbench: {testbench}")
            return []
        
        return list(self.testbenches[testbench].get("tests", {}).keys()) 