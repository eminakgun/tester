from typing import Dict, List, Optional, Any
import os
import subprocess
import logging
import shutil
from pathlib import Path

from build_systems.base import BuildSystemBase
from build_systems.makefile.templates import MakefileTemplateFactory

logger = logging.getLogger(__name__)


class MakefileBuildSystem(BuildSystemBase):
    """Build system implementation that uses Makefiles."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the Makefile build system with configuration.

        Args:
            config: Dictionary containing build system configuration
        """
        super().__init__(config)
        self.makefile_path = config.get("makefile_path", ".")
        self.make_command = config.get("make_command", "make")
        self.template_type = config.get("template_type", "uvm")
        self.use_custom_makefile = config.get("use_custom_makefile", True)
        self.template_config = config.get("template_config", {})
        self.generated_makefile_path = config.get("generated_makefile_path")
        
        # Generate Makefile if needed
        if not self.use_custom_makefile:
            self._generate_makefile()

    def _generate_makefile(self) -> None:
        """Generate a Makefile from template."""
        if not self.generated_makefile_path:
            self.generated_makefile_path = os.path.join(
                self.makefile_path, "Makefile"
            )
        
        # Create makefile directory if it doesn't exist
        makefile_dir = os.path.dirname(self.generated_makefile_path)
        os.makedirs(makefile_dir, exist_ok=True)
        
        # Generate the makefile
        try:
            template = MakefileTemplateFactory.create(self.template_type, self.template_config)
            template.generate(self.generated_makefile_path)
            
            # Update makefile_path to use the generated makefile
            self.makefile_path = os.path.dirname(self.generated_makefile_path)
            logger.info(f"Generated Makefile at {self.generated_makefile_path}")
        except Exception as e:
            logger.error(f"Failed to generate Makefile: {e}")
            raise

    def _run_make_command(self, target: str, options: Optional[Dict[str, Any]] = None) -> bool:
        """Run a make command with the given target and options.

        Args:
            target: Make target to run
            options: Additional make options as variable=value pairs

        Returns:
            bool: True if command was successful, False otherwise
        """
        cmd = [self.make_command, "-C", self.makefile_path, target]
        
        if options:
            for key, value in options.items():
                cmd.append(f"{key}={value}")
        
        logger.debug(f"Running command: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Make command failed: {e}")
            logger.error(f"Stdout: {e.stdout.decode('utf-8')}")
            logger.error(f"Stderr: {e.stderr.decode('utf-8')}")
            return False

    def build(self, testbench: str, options: Optional[Dict[str, Any]] = None) -> bool:
        """Build the testbench using make.

        Args:
            testbench: Name of the testbench to build
            options: Additional build options

        Returns:
            bool: True if build was successful, False otherwise
        """
        build_options = options or {}
        build_options["TESTBENCH"] = testbench
        
        # Handle debug mode
        if "debug" in build_options:
            build_options["DEBUG"] = "1" if build_options.pop("debug") else "0"
            
        # Handle incremental build
        if "incremental" in build_options and not build_options.pop("incremental"):
            logger.info(f"Performing clean build for testbench {testbench}")
            self.clean(testbench)
        
        # Check if testbench has a custom build command
        targets = self.config.get("targets", {})
        testbench_config = targets.get(testbench, {})
        
        if "build_command" in testbench_config:
            # Use the custom build command
            custom_cmd = testbench_config["build_command"]
            logger.info(f"Using custom build command: {custom_cmd}")
            
            # Parse the command to extract the make target
            # Assuming format like "make build_testbench1"
            parts = custom_cmd.split()
            if len(parts) > 1 and parts[0].lower() == "make":
                target = parts[1]
                return self._run_make_command(target, build_options)
            else:
                logger.error(f"Invalid build command format: {custom_cmd}")
                return False
        else:
            # Use default "build" target
            return self._run_make_command("build", build_options)

    def run(self, testbench: str, test: str, options: Optional[Dict[str, Any]] = None) -> bool:
        """Run a specific test for the given testbench using make.

        Args:
            testbench: Name of the testbench
            test: Name of the test to run
            options: Additional run options

        Returns:
            bool: True if test run was successful, False otherwise
        """
        run_options = options or {}
        run_options["TESTBENCH"] = testbench
        run_options["TEST"] = test
        
        # Handle debug mode
        if "debug" in run_options:
            run_options["DEBUG"] = "1" if run_options.pop("debug") else "0"
            
        # Handle coverage
        if "coverage" in run_options:
            run_options["COVERAGE"] = "1" if run_options.pop("coverage") else "0"
            
        # Handle seed
        if "seed" in run_options:
            run_options["SEED"] = str(run_options.pop("seed"))
            
        # Handle verbosity
        if "verbosity" in run_options:
            verbosity = run_options.pop("verbosity").upper()
            if not verbosity.startswith("UVM_"):
                verbosity = f"UVM_{verbosity}"
            run_options["VERBOSITY"] = verbosity
        
        # Handle runtime arguments
        if "runtime_args" in run_options:
            runtime_args = run_options.pop("runtime_args")
            run_options["RUNTIME_ARGS"] = " ".join(runtime_args)
        
        # Check if testbench has a separate build command
        targets = self.config.get("targets", {})
        testbench_config = targets.get(testbench, {})
        
        if "build_command" in testbench_config:
            # If there's a build command, run build first
            logger.info(f"Building testbench {testbench} before running test")
            if not self.build(testbench, run_options):
                logger.error(f"Build failed for testbench {testbench}")
                return False
        else:
            # No build command - assume run command handles both build and run
            logger.info(f"No separate build command for {testbench}, assuming run command handles build")
        
        return self._run_make_command("run", run_options)

    def clean(self, testbench: str) -> bool:
        """Clean the testbench using make clean.

        Args:
            testbench: Name of the testbench to clean

        Returns:
            bool: True if clean was successful, False otherwise
        """
        clean_options = {"TESTBENCH": testbench}
        
        return self._run_make_command("clean", clean_options)

    def get_available_testbenches(self) -> List[str]:
        """Get a list of available testbenches from Makefile.

        Returns:
            List[str]: List of testbench names
        """
        # This implementation assumes there's a make target 'list-testbenches'
        # that outputs available testbenches one per line
        cmd = [self.make_command, "-C", self.makefile_path, "list-testbenches"]
        
        try:
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            testbenches = result.stdout.decode('utf-8').strip().split('\n')
            return [tb.strip() for tb in testbenches if tb.strip()]
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get testbenches: {e}")
            return []

    def get_available_tests(self, testbench: str) -> List[str]:
        """Get a list of available tests for a testbench from Makefile.

        Args:
            testbench: Name of the testbench

        Returns:
            List[str]: List of test names
        """
        # This implementation assumes there's a make target 'list-tests'
        # that outputs available tests one per line
        cmd = [self.make_command, "-C", self.makefile_path, "list-tests", f"TESTBENCH={testbench}"]
        
        try:
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            tests = result.stdout.decode('utf-8').strip().split('\n')
            return [test.strip() for test in tests if test.strip()]
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get tests for {testbench}: {e}")
            return [] 