# Quick Start Guide

This guide will help you get started with Tester quickly by running your first test.

## Basic Usage

After installing Tester, you can run your first test with just a few commands:

```bash
# Navigate to your project directory
cd your_project_directory

# Create a basic configuration file
cat > tester.yml << EOF
build_system: makefile
makefile_path: .
make_command: make
use_custom_makefile: true
default_testbench: my_testbench

testbenches:
  my_testbench:
    tests:
      basic_test:
        runtime_args:
          - +UVM_TESTNAME=basic_test
          - +TIMEOUT=1000
EOF

# Run your first test
python -m tester run my_testbench basic_test
```

## Command Line Interface

```bash
# List available testbenches
python -m tester list-testbenches

# List available tests for a testbench
python -m tester list-tests my_testbench

# Build a testbench
python -m tester build my_testbench

# Run a specific test
python -m tester run my_testbench basic_test

# Use a specific simulator
python -m tester --simulator questa run my_testbench basic_test

# Clean a testbench
python -m tester clean my_testbench
```

## Common Options
Tester supports various options for customizing test execution:

```bash
# Run with debug enabled
python -m tester run my_testbench basic_test --debug

# Run with coverage enabled
python -m tester run my_testbench basic_test --coverage

# Set a specific seed
python -m tester run my_testbench basic_test --seed 12345

# Set UVM verbosity
python -m tester run my_testbench basic_test --verbosity HIGH

# Pass custom runtime arguments
python -m tester run my_testbench basic_test --runtime-args "+MY_ARG=value1"
```

## Next Steps
- [Configuration Guide](../configuration/index.md) - Learn how to configure the tool for your project
- [Build Systems](../build-systems/index.md) - Learn about different build system options
- [Simulators](../simulators/index.md) - Learn about supported simulators
