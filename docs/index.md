# Tester

A flexible Python tool for automating UVM testbench execution, simplifying regression testing, and supporting multiple simulators and build systems.

## Overview

This tool provides a unified interface for running UVM (Universal Verification Methodology) testbenches and regressions across different simulators and build systems. It replaces manual Makefile management with a configuration-driven approach that's more maintainable and extensible.

## Key Features

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

## Quick Links

- [Installation](getting-started/installation.md)
- [Quick Start Guide](getting-started/quick-start.md)
- [Configuration Guide](getting-started/configuration.md)
- [Command Line Interface](user-guide/cli.md)
- [Architecture Overview](development/architecture.md)