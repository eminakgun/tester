# Changelog

## [Unreleased]

### Added
- Basic CLI framework with Click
- Configuration file support (YAML-based)
  - Support for both tester.yml and config.yml
  - Flexible configuration structure
  - Validation and error handling
- Multiple build system support
  - Makefile integration
  - Edalize integration
- Test management features
  - List available testbenches
  - List available tests
  - Run specific tests with options
  - Build testbenches
  - Clean build artifacts
- Command line features
  - Verbose logging option
  - Custom config file path
  - Runtime arguments for tests
  - Test verbosity levels
  - Coverage options
  - Debug build options
  - Seed specification for tests
- Example configurations
  - Custom Makefile example
  - Generated Makefile example
  - Edalize integration example
  - Minimal configuration example
- Comprehensive test coverage (97%)
  - Unit tests for all major components
  - Error handling tests
  - Configuration parsing tests
  - CLI interaction tests

### Changed
- Improved error handling and reporting
- Enhanced configuration file search logic
- Better test output formatting

### Fixed
- Path handling in configuration files
- Directory cleanup after tests
- Error message propagation 