# Configuration Examples

This directory contains example configurations for different use cases:

1. `configs/custom_makefile.yml`: Using an existing Makefile
2. `configs/generated_makefile.yml`: Generating a Makefile from template
3. `configs/edalize.yml`: Using Edalize for tool integration
4. `configs/minimal.yml`: Minimal working configuration

## Usage

Copy the appropriate example to your project's root as `config.yml` and modify as needed:

```bash
cp examples/configs/custom_makefile.yml config.yml
```

## Configuration Types

### Custom Makefile
Use when you have an existing Makefile and want to integrate it with the tool.

### Generated Makefile
Use when you want the tool to generate a Makefile based on your configuration.

### Edalize
Use when you want to use Edalize for direct tool integration without Makefiles.

### Minimal
Use as a starting point for simple projects.

## Notes

1. All paths in the configuration files are relative to the project root
2. The `default_testbench` setting is optional but recommended
3. Runtime arguments can be specified per test or added via command line 