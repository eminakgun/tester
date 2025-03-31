# Tester

A flexible Python tool for automating UVM testbench execution, simplifying regression testing, and supporting multiple simulators and build systems.

## Overview

This tool provides a unified interface for running UVM (Universal Verification Methodology) testbenches and regressions across different simulators and build systems. It replaces manual Makefile management with a configuration-driven approach that's more maintainable and extensible.

## Features

- **Multiple Simulator Support**: Works with VCS, Questa, and Xcelium
- **Configurable Build System**: Supports custom Makefiles and generated templates
- **Test Organization**: Manage testbenches and tests with YAML configuration
- **Flexible Build Configuration**
  - Support for separate build/run commands
  - Combined build/run command support
  - Automatic build dependency handling
- **Enhanced Test Management**
  - Runtime argument handling
  - Test-specific configurations
  - Build failure detection and reporting
- **Makefile Integration**: Integrates with existing Makefile-based workflows
- **Configuration-based**: Uses YAML for testbench and test configuration
- **Regression Management**: Run multiple tests in parallel with smart resource management
- **Extensible Architecture**: Easily add new simulators or build systems
- **Unified CLI**: Consistent command-line interface regardless of backend simulator or build system
- **Results Collection**: Parse and analyze simulation results

## Architecture

The tool is built with a modular architecture that separates concerns and provides clean interfaces between components: 

+-------------+
                | CLI Command |
                +------+------+
                       |
                       v
+----------+    +------+------+    +-----------+
| Config   +--->+ Test Runner +--->+ Reporter  |
+----------+    +------+------+    +-----------+
                       |
                       |
        +-------------+-------------+
        |                           |
        v                           v
+-------+--------+         +-------+--------+
| Build System   |         | Simulator      |
| Interface      |         | Interface      |
+----------------+         +----------------+
        |                           |
        |                           |
+-------v--------+         +-------v--------+
| - Makefile     |         | - VCS          |
| - Direct Build |         | - Xcelium      |
+----------------+         | - Questa       |
                           | - Custom       |
                           +----------------+



### Key Components

- **Config Manager**: Handles YAML configuration loading and access
- **Test Runner**: Orchestrates test execution and manages resources
- **Build System Interface**: Abstraction for different build systems
- **Simulator Interface**: Abstraction for simulator commands
- **Adapters**: Connect simulators to the build system interface
- **Results Parser**: Analyzes simulator outputs

## Installation

### Prerequisites

- Python 3.6+
- PyYAML (`pip install pyyaml`)
- Access to UVM simulators (VCS, Questa, or Xcelium)

### Install Steps

```bash
Clone the repository
git clone https://github.com/yourusername/uvm-runner.git
Install dependencies
pip install -r requirements.txt
```

### Usage

## CLI Examples

# List available testbenches
python -m tester list

# List tests in a specific testbench
python -m tester list --testbench my_testbench

# Run a specific test
python -m tester run --testbench my_testbench --test basic_test

# Run a regression
python -m tester regression --name smoke --parallel 4

# Use a specific simulator
python -m tester --simulator questa run --testbench my_testbench --test basic_test

# Use Makefile-based build
python -m tester --simulator makefile run --testbench makefile_testbench --test basic_make_test 

## Build Systems

### Makefile

When using the Makefile build system, your Makefile must implement certain targets and support specific variables. Here's what you need to include:

### Required Make Targets

1. `build`: Compile the testbench
   ```make
   build:
       $(SIMULATOR) $(COMPILE_FLAGS) $(TESTBENCH_FILES)
   ```

2. `run`: Execute a specific test
   ```make
   run:
       $(SIMULATOR) $(SIM_FLAGS) $(RUNTIME_ARGS)
   ```

3. `clean`: Clean build artifacts
   ```make
   clean:
       rm -rf $(BUILD_DIR)/$(TESTBENCH)/*
   ```

4. `list-testbenches`: List available testbenches (one per line)
   ```make
   list-testbenches:
       @echo $(TESTBENCHES)
   ```

5. `list-tests`: List available tests for a testbench (one per line)
   ```make
   list-tests:
       @echo $(TESTS_$(TESTBENCH))
   ```

### Required Make Variables

Your Makefile must handle these variables that the tool will pass:

1. `TESTBENCH`: Name of the testbench to build/run
   ```make
   TESTBENCH ?= default_testbench
   ```

2. `TEST`: Name of the test to run
   ```make
   TEST ?= basic_test
   ```

3. `RUNTIME_ARGS`: Runtime arguments for the simulator
   ```make
   RUNTIME_ARGS ?=
   ```

4. `DEBUG`: Enable debug mode (0 or 1)
   ```make
   DEBUG ?= 0
   ifeq ($(DEBUG),1)
       COMPILE_FLAGS += -debug_all
   endif
   ```

5. `COVERAGE`: Enable coverage collection (0 or 1)
   ```make
   COVERAGE ?= 0
   ifeq ($(COVERAGE),1)
       COMPILE_FLAGS += -coverage
       SIM_FLAGS += -coverage
   endif
   ```

6. `SEED`: Random seed for simulation
   ```make
   SEED ?= random
   SIM_FLAGS += -ntb_random_seed $(SEED)
   ```

7. `VERBOSITY`: UVM verbosity level
   ```make
   VERBOSITY ?= UVM_MEDIUM
   RUNTIME_ARGS += +UVM_VERBOSITY=$(VERBOSITY)
   ```

### Example Makefile Structure

Here's a minimal example of a compliant Makefile:

```make
# Default values
TESTBENCH ?= default_testbench
TEST ?= basic_test
SIMULATOR ?= vcs
BUILD_DIR ?= build
RUNTIME_ARGS ?=
DEBUG ?= 0
COVERAGE ?= 0
SEED ?= random
VERBOSITY ?= UVM_MEDIUM

# Base flags
COMPILE_FLAGS = -sverilog -full64
SIM_FLAGS = -R

# Debug mode
ifeq ($(DEBUG),1)
    COMPILE_FLAGS += -debug_all
endif

# Coverage
ifeq ($(COVERAGE),1)
    COMPILE_FLAGS += -coverage
    SIM_FLAGS += -coverage
endif

# Available testbenches and tests
TESTBENCHES = testbench1 testbench2
TESTS_testbench1 = test1 test2 test3
TESTS_testbench2 = basic_test extended_test

# Main targets
build:
	@mkdir -p $(BUILD_DIR)/$(TESTBENCH)
	$(SIMULATOR) $(COMPILE_FLAGS) -o $(BUILD_DIR)/$(TESTBENCH)/simv $(TESTBENCH_FILES)

run: build
	cd $(BUILD_DIR)/$(TESTBENCH) && ./simv $(SIM_FLAGS) \
		+UVM_TESTNAME=$(TEST) \
		+UVM_VERBOSITY=$(VERBOSITY) \
		-ntb_random_seed $(SEED) \
		$(RUNTIME_ARGS)

clean:
	rm -rf $(BUILD_DIR)/$(TESTBENCH)

# List targets
list-testbenches:
	@echo $(TESTBENCHES)

list-tests:
	@echo $(TESTS_$(TESTBENCH))

.PHONY: build run clean list-testbenches list-tests
```

### Configuration

The tool looks for configuration files in the following order:

1. File specified with `--config` option
2. `tester.yml` in current directory
3. `config.yml` in current directory

```bash
# Use specific config file
tester --config my_config.yml run basic_test

# Use default config file (tester.yml or config.yml)
tester run basic_test
```

### Build System Options
You can configure testbenches in two ways:

1. Separate build and run commands:
```yaml
targets:
  testbench1:
    build_command: make build_testbench1
    run_command: make sim_testbench1
```

2. Combined build/run command:
```yaml
targets:
  testbench2:
    run_command: make sim_testbench2  # Handles both build and run
```

### Example Configurations

The tool includes several example configurations for different use cases:

1. **Custom Makefile** (`examples/configs/custom_makefile.yml`)
   - Use when you have an existing Makefile and want to integrate it with the tool
   - Preserves your existing build system while adding tool features

2. **Generated Makefile** (`examples/configs/generated_makefile.yml`)
   - Use when you want the tool to generate a Makefile based on your configuration
   - Best for new projects or standardized setups

3. **Edalize** (`examples/configs/edalize.yml`)
   - Use when you want to use Edalize for direct tool integration without Makefiles
   - Provides simulator-agnostic configuration

4. **Minimal** (`examples/configs/minimal.yml`)
   - Use as a starting point for simple projects
   - Contains only essential settings

To use an example configuration:

```bash
cp examples/configs/custom_makefile.yml config.yml
```

**Configuration Notes:**
- All paths in configuration files are relative to the project root
- The `default_testbench` setting is optional but recommended
- Runtime arguments can be specified per test or added via command line

Example configuration with test-specific runtime arguments:

```yaml
build_system: makefile
makefile_path: .
make_command: make
use_custom_makefile: true
default_testbench: my_testbench
template_config:
  simulator: vcs
  testbenches:
    my_testbench:
      tests:
        basic_test:
          runtime_args:
            - +UVM_TESTNAME=basic_test
            - +TIMEOUT=1000
        extended_test:
          runtime_args:
            - +UVM_TESTNAME=extended_test
            - +TIMEOUT=2000
```

### Command Line Usage

Run a test with additional runtime arguments:

```bash
# Run with config-defined arguments using default testbench
tester run basic_test

# Explicitly specify testbench
tester run my_testbench basic_test

# Add more runtime arguments
tester run basic_test \
    --runtime-args "+MY_ARG=value1" \
    --runtime-args "+ANOTHER_ARG=value2"

# List tests for default testbench
tester list-tests

# Build default testbench
tester build
```

## Notes

1. The tool will automatically handle the combination of:
   - Default arguments from your Makefile
   - Test-specific arguments from config.yml
   - Command-line runtime arguments

2. If no testbench is specified:
   - First checks for `default_testbench` in config.yml
   - If not set, uses the first testbench found in config
   - Raises an error if no testbench can be determined

3. Make sure your Makefile properly escapes special characters in `RUNTIME_ARGS`

4. The order of runtime arguments will be:
   - Makefile defaults
   - Configuration file arguments
   - Command line arguments

5. For UVM testbenches, always ensure `+UVM_TESTNAME` is set correctly

## Riviera-Pro Support

To use Riviera-Pro for simulation:

1. Create a configuration file (see `examples/configs/riviera_testbenches.yml`)
2. Organize your testbenches in the `tb/` directory with names matching your make targets
3. Run specific testbenches with `make sim_testbench_name`
4. Run all testbenches with `make all_tests`

## Roadmap

### Planned Features
- [ ] Parallel test execution
- [ ] Test result collection and reporting
- [ ] Test suite organization
- [ ] Test dependencies and ordering
- [ ] Coverage report aggregation
- [ ] CI/CD integration examples
- [ ] Plugin system for custom build systems
- [ ] Web interface for test management
- [ ] Test result visualization
- [ ] Resource monitoring during test execution

### Known Limitations
- Currently supports single test execution only
- Limited test result parsing
- No built-in test scheduling
- Basic build system integration
- Manual configuration required for complex setups