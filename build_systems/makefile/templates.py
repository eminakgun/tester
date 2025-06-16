import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class MakefileTemplate:
    """Base class for Makefile templates."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the template with configuration.

        Args:
            config: Dictionary containing template configuration
        """
        self.config = config
        self.output_dir = config.get("output_dir", ".")

    def generate(self, output_path: Optional[str] = None) -> str:
        """Generate the Makefile content.

        Args:
            output_path: Optional path to write the Makefile

        Returns:
            str: The generated Makefile content
        """
        content = self._generate_content()

        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w") as f:
                f.write(content)
            logger.info(f"Generated Makefile at {output_path}")

        return content

    def _generate_content(self) -> str:
        """Generate the actual Makefile content.

        Returns:
            str: The Makefile content
        """
        raise NotImplementedError("Subclasses must implement _generate_content")


class UVMTestbenchMakefile(MakefileTemplate):
    """Template for UVM testbench Makefiles."""

    def _generate_content(self) -> str:
        """Generate UVM testbench Makefile content.

        Returns:
            str: The Makefile content
        """
        simulator = self.config.get("simulator", "vcs")
        includes = self.config.get("includes", [])
        defines = self.config.get("defines", {})
        src_files = self.config.get("src_files", [])
        tb_files = self.config.get("tb_files", [])
        testbenches = self.config.get("testbenches", {})
        build_options = self.config.get("build_options", {})
        run_options = self.config.get("run_options", {})

        # Start with header and variable definitions
        content = [
            "# Generated UVM Testbench Makefile",
            "# Do not edit manually",
            "",
            "# Default variables",
            f"SIMULATOR ?= {simulator}",
            "TESTBENCH ?= $(error TESTBENCH is not set)",
            "TEST ?= $(error TEST is not set)",
            "SEED ?= random",
            "DEBUG ?= 0",
            "COVERAGE ?= 0",
            "VERBOSITY ?= UVM_MEDIUM",
            "",
            "# Directory structure",
            "SIM_DIR ?= ./sim",
            "BUILD_DIR ?= $(SIM_DIR)/build/$(TESTBENCH)",
            "RESULTS_DIR ?= $(SIM_DIR)/results/$(TESTBENCH)/$(TEST)",
            "",
            "# Include paths",
        ]

        # Add include paths
        for include in includes:
            content.append(f"INCLUDE_DIRS += {include}")

        content.append("")
        content.append("# Define macros")

        # Add defines
        for name, value in defines.items():
            if value:
                content.append(f"DEFINES += +define+{name}={value}")
            else:
                content.append(f"DEFINES += +define+{name}")

        content.append("")
        content.append("# Source files")

        # Add source files
        for src_file in src_files:
            content.append(f"SRC_FILES += {src_file}")

        content.append("")
        content.append("# Testbench files")

        # Add testbench files
        for tb_file in tb_files:
            content.append(f"TB_FILES += {tb_file}")

        content.append("")

        # Add simulator-specific sections
        if simulator.lower() == "vcs":
            content.extend(self._generate_vcs_section(build_options, run_options))
        elif simulator.lower() == "questa":
            content.extend(self._generate_questa_section(build_options, run_options))
        elif simulator.lower() == "xcelium":
            content.extend(self._generate_xcelium_section(build_options, run_options))
        else:
            content.append(f"# Unsupported simulator: {simulator}")

        # Add common targets
        content.extend(
            [
                "",
                "# Common targets",
                ".PHONY: all build run clean help list-testbenches list-tests",
                "",
                "all: build run",
                "",
                "build:",
                "\t@mkdir -p $(BUILD_DIR)",
                "\t$(BUILD_CMD)",
                "",
                "run:",
                "\t@mkdir -p $(RESULTS_DIR)",
                "\t$(RUN_CMD)",
                "",
                "clean:",
                "\trm -rf $(BUILD_DIR)",
                "",
                "help:",
                '\t@echo "UVM Testbench Makefile"',
                '\t@echo "Usage:"',
                '\t@echo "  make build TESTBENCH=<testbench>"',
                '\t@echo "  make run TESTBENCH=<testbench> TEST=<test> [SEED=<seed>] [DEBUG=0|1] [COVERAGE=0|1]"',
                '\t@echo "  make clean TESTBENCH=<testbench>"',
                '\t@echo "  make list-testbenches"',
                '\t@echo "  make list-tests TESTBENCH=<testbench>"',
                "",
            ]
        )

        # Add testbench discovery target
        content.extend(
            [
                "list-testbenches:",
            ]
        )

        for tb_name in testbenches.keys():
            content.append(f'\t@echo "{tb_name}"')

        content.append("")

        # Add tests discovery target (uses conditional logic)
        content.extend(
            [
                "list-tests:",
            ]
        )

        if testbenches:
            content.append('\t@case "$(TESTBENCH)" in \\')

            for tb_name, tb_data in testbenches.items():
                content.append(f"\t\t{tb_name}) \\")
                if "tests" in tb_data and tb_data["tests"]:
                    for test in tb_data["tests"]:
                        content.append(f'\t\t\techo "{test}"; \\')
                content.append("\t\t\t;; \\")

            content.append("\t\t*) \\")
            content.append('\t\t\techo "Unknown testbench: $(TESTBENCH)"; \\')
            content.append("\t\t\texit 1; \\")
            content.append("\t\t\t;; \\")
            content.append("\tesac")

        return "\n".join(content)

    def _generate_vcs_section(self, build_options: Dict[str, Any], run_options: Dict[str, Any]) -> List[str]:
        """Generate VCS-specific Makefile section.

        Args:
            build_options: VCS build options
            run_options: VCS run options

        Returns:
            List[str]: VCS-specific Makefile lines
        """
        vcs_home = build_options.get("vcs_home", "$(VCS_HOME)")
        compile_args = build_options.get("compile_args", "-full64 -sverilog -timescale=1ns/1ps -CFLAGS -DVCS")
        debug_args = "-debug_access+all" if build_options.get("debug", True) else ""
        coverage_args = "-cm line+cond+fsm+branch+tgl" if build_options.get("coverage", True) else ""

        content = [
            "# VCS-specific settings",
            "ifeq ($(SIMULATOR),vcs)",
            f"  VCS_HOME ?= {vcs_home}",
            "  VCS = $(VCS_HOME)/bin/vcs",
            "  SIMV = $(BUILD_DIR)/simv",
            "",
            "  # Debug settings",
            "  ifeq ($(DEBUG),1)",
            f"    DEBUG_ARGS = {debug_args}",
            "  else",
            "    DEBUG_ARGS =",
            "  endif",
            "",
            "  # Coverage settings",
            "  ifeq ($(COVERAGE),1)",
            f"    COVERAGE_ARGS = {coverage_args}",
            "  else",
            "    COVERAGE_ARGS =",
            "  endif",
            "",
            "  # Build command",
            f"  BUILD_CMD = $(VCS) -o $(SIMV) $(SRC_FILES) $(TB_FILES) \\",
            f"              $(INCLUDE_DIRS) $(DEFINES) \\",
            f"              {compile_args} \\",
            "              $(DEBUG_ARGS) $(COVERAGE_ARGS) \\",
            "              -ntb_opts uvm-1.2",
            "",
            "  # Run command",
            "  RUN_CMD = $(SIMV) -l $(RESULTS_DIR)/sim.log \\",
            "            +UVM_TESTNAME=$(TEST) \\",
            "            +UVM_VERBOSITY=$(VERBOSITY) \\",
            "            +ntb_random_seed=$(SEED) \\",
            "            $(if $(COVERAGE),,-cm_dir $(RESULTS_DIR)/coverage)",
            "endif",
        ]

        return content

    def _generate_questa_section(self, build_options: Dict[str, Any], run_options: Dict[str, Any]) -> List[str]:
        """Generate Questa-specific Makefile section.

        Args:
            build_options: Questa build options
            run_options: Questa run options

        Returns:
            List[str]: Questa-specific Makefile lines
        """
        questa_home = build_options.get("questa_home", "$(QUESTA_HOME)")
        compile_args = build_options.get("compile_args", "-64 -sv -timescale=1ns/1ps -mfcu +acc=rmb")
        debug_args = "-debugdb" if build_options.get("debug", True) else ""
        coverage_args = "+cover=bcestf" if build_options.get("coverage", True) else ""

        content = [
            "# Questa-specific settings",
            "ifeq ($(SIMULATOR),questa)",
            f"  QUESTA_HOME ?= {questa_home}",
            "  VLOG = $(QUESTA_HOME)/bin/vlog",
            "  VSIM = $(QUESTA_HOME)/bin/vsim",
            "  VLIB = $(QUESTA_HOME)/bin/vlib",
            "  VMAP = $(QUESTA_HOME)/bin/vmap",
            "",
            "  # Debug settings",
            "  ifeq ($(DEBUG),1)",
            f"    DEBUG_ARGS = {debug_args}",
            "  else",
            "    DEBUG_ARGS =",
            "  endif",
            "",
            "  # Coverage settings",
            "  ifeq ($(COVERAGE),1)",
            f"    COVERAGE_ARGS = {coverage_args}",
            "  else",
            "    COVERAGE_ARGS =",
            "  endif",
            "",
            "  # Build command",
            "  BUILD_CMD = cd $(BUILD_DIR) && \\",
            "             $(VLIB) work && \\",
            "             $(VMAP) work work && \\",
            f"             $(VLOG) $(SRC_FILES) $(TB_FILES) \\",
            f"             $(INCLUDE_DIRS) $(DEFINES) \\",
            f"             {compile_args} \\",
            "             $(DEBUG_ARGS) $(COVERAGE_ARGS) \\",
            "             -suppress 2263 \\",
            "             +define+UVM_CMDLINE_NO_DPI \\",
            "             +define+UVM_REGEX_NO_DPI",
            "",
            "  # Run command",
            "  RUN_CMD = cd $(BUILD_DIR) && \\",
            '           $(VSIM) -batch -do "run -all; quit -f" \\',
            "           -l $(RESULTS_DIR)/sim.log \\",
            "           work.top \\",
            "           +UVM_TESTNAME=$(TEST) \\",
            "           +UVM_VERBOSITY=$(VERBOSITY) \\",
            "           -sv_seed $(SEED) \\",
            "           $(if $(COVERAGE),-coverage)",
            "endif",
        ]

        return content

    def _generate_xcelium_section(self, build_options: Dict[str, Any], run_options: Dict[str, Any]) -> List[str]:
        """Generate Xcelium-specific Makefile section.

        Args:
            build_options: Xcelium build options
            run_options: Xcelium run options

        Returns:
            List[str]: Xcelium-specific Makefile lines
        """
        xcelium_home = build_options.get("xcelium_home", "$(XCELIUM_HOME)")
        compile_args = build_options.get("compile_args", "-64bit -sv -timescale 1ns/1ps -access +rwc")
        debug_args = "-debug" if build_options.get("debug", True) else ""
        coverage_args = "-coverage all -covoverwrite" if build_options.get("coverage", True) else ""

        content = [
            "# Xcelium-specific settings",
            "ifeq ($(SIMULATOR),xcelium)",
            f"  XCELIUM_HOME ?= {xcelium_home}",
            "  XRUN = $(XCELIUM_HOME)/bin/xrun",
            "",
            "  # Debug settings",
            "  ifeq ($(DEBUG),1)",
            f"    DEBUG_ARGS = {debug_args}",
            "  else",
            "    DEBUG_ARGS =",
            "  endif",
            "",
            "  # Coverage settings",
            "  ifeq ($(COVERAGE),1)",
            f"    COVERAGE_ARGS = {coverage_args}",
            "  else",
            "    COVERAGE_ARGS =",
            "  endif",
            "",
            "  # Build and run combined for Xcelium",
            "  BUILD_CMD = $(XRUN) -elaborate \\",
            f"             $(SRC_FILES) $(TB_FILES) \\",
            f"             $(INCLUDE_DIRS) $(DEFINES) \\",
            f"             {compile_args} \\",
            "             $(DEBUG_ARGS) $(COVERAGE_ARGS) \\",
            "             -uvmhome CDNS-1.2",
            "",
            "  # Run command",
            "  RUN_CMD = $(XRUN) -R \\",
            "           -xmlibdirname $(BUILD_DIR) \\",
            "           -l $(RESULTS_DIR)/sim.log \\",
            "           +UVM_TESTNAME=$(TEST) \\",
            "           +UVM_VERBOSITY=$(VERBOSITY) \\",
            "           -svseed $(SEED)",
            "endif",
        ]

        return content


class RivieraProMakefile(MakefileTemplate):
    """Template for Riviera-Pro Makefiles."""

    def _generate_content(self) -> str:
        """Generate Riviera-Pro Makefile content.

        Returns:
            str: The Makefile content
        """
        # Get configuration values
        vsim = self.config.get("variables", {}).get("VSIM", "vsim")
        vlog = self.config.get("variables", {}).get("VLOG", "vlog")
        vsimflags = self.config.get("variables", {}).get("VSIMFLAGS", '-c -do "run -all; exit;"')

        # Get directory structure
        rtl_dir = self.config.get("directories", {}).get("rtl", "rtl")
        tb_dir = self.config.get("directories", {}).get("testbench", "tb")
        build_dir = self.config.get("directories", {}).get("build", "build")
        results_dir = self.config.get("directories", {}).get("results", "results")

        content = [
            "# Generated Riviera-Pro Makefile",
            "# Do not edit manually",
            "",
            "# Simulator settings",
            f"VSIM = {vsim}",
            f"VLOG = {vlog}",
            f"VSIMFLAGS = {vsimflags}",
            "",
            "# Directory structure",
            f"RTL_DIR = {rtl_dir}",
            f"TB_DIR = {tb_dir}",
            f"BUILD_DIR = {build_dir}",
            f"RESULTS_DIR = {results_dir}",
            "",
            "# Source files",
            "RTL_SRCS = $(wildcard $(RTL_DIR)/*.v)",
            "TB_SRCS = $(wildcard $(TB_DIR)/*.sv)",
            "",
            "# Default variables",
            "TESTBENCH ?= $(error TESTBENCH is not set)",
            "TEST ?= $(error TEST is not set)",
            "SEED ?= random",
            "DEBUG ?= 0",
            "COVERAGE ?= 0",
            "VERBOSITY ?= UVM_MEDIUM",
            "",
            "# Targets",
            ".PHONY: build run clean list-testbenches list-tests",
            "",
            "build:",
            "\t@mkdir -p $(BUILD_DIR)",
            "\t$(VLOG) $(RTL_SRCS) $(TB_DIR)/$(TESTBENCH).sv",
            "",
            "run: build",
            "\t@mkdir -p $(RESULTS_DIR)/$(TESTBENCH)",
            "\t$(VSIM) $(VSIMFLAGS) \\",
            "\t\t-l $(RESULTS_DIR)/$(TESTBENCH)/$(TEST).log \\",
            "\t\t+UVM_TESTNAME=$(TEST) \\",
            "\t\t+UVM_VERBOSITY=$(VERBOSITY) \\",
            "\t\t$(TESTBENCH)",
            "",
            "clean:",
            "\trm -rf $(BUILD_DIR) $(RESULTS_DIR) work transcript vsim.wlf",
            "",
            "list-testbenches:",
        ]

        # Add testbenches from config
        for tb in self.config.get("template_config", {}).get("testbenches", {}):
            content.append(f'\t@echo "{tb}"')

        content.extend(["", "list-tests:", '\t@case "$(TESTBENCH)" in \\'])

        # Add tests for each testbench
        testbenches = self.config.get("template_config", {}).get("testbenches", {})
        for tb_name, tb_data in testbenches.items():
            content.append(f"\t\t{tb_name}) \\")
            if "tests" in tb_data:
                for test in tb_data["tests"]:
                    content.append(f'\t\t\techo "{test}"; \\')
            content.append("\t\t\t;; \\")

        content.extend(
            ["\t\t*) \\", '\t\t\techo "Unknown testbench: $(TESTBENCH)"; \\', "\t\t\texit 1; \\", "\t\t\t;; \\", "\tesac"]
        )

        return "\n".join(content)


class MakefileTemplateFactory:
    """Factory class for creating Makefile templates."""

    @staticmethod
    def create(template_type: str, config: Dict[str, Any]) -> MakefileTemplate:
        """Create a Makefile template of the given type.

        Args:
            template_type: Type of template to create
            config: Template configuration

        Returns:
            MakefileTemplate: The created template

        Raises:
            ValueError: If the template type is not supported
        """
        if template_type.lower() == "uvm":
            return UVMTestbenchMakefile(config)
        elif template_type.lower() == "riviera-pro":
            return RivieraProMakefile(config)
        else:
            raise ValueError(f"Unsupported Makefile template type: {template_type}")


RIVIERA_TEMPLATE = """
# Riviera-Pro specific settings
VSIM = vsim
VLOG = vlog
VSIMFLAGS = -c -do "run -all; exit;"

# Common source files and directories
RTL_SRCS = $(wildcard rtl/*.v)
TB_SRCS = $(wildcard tb/*.sv)

# Testbench targets
.PHONY: sim_tb1 sim_tb2 all_tests clean

sim_%: $(RTL_SRCS) tb/%.sv
	$(VLOG) $(RTL_SRCS) $<
	$(VSIM) $(VSIMFLAGS) $*

all_tests: sim_tb1 sim_tb2

clean:
	rm -rf work transcript vsim.wlf
"""


def get_makefile_template(build_config):
    if build_config.get("variables", {}).get("SIMULATOR") == "riviera-pro":
        return RIVIERA_TEMPLATE
    # ... existing code ...
