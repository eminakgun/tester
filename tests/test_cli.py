import os
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import click
from click.testing import CliRunner
import yaml
import logging

from cli import cli, find_config_file, load_config, get_default_testbench, get_build_system
from build_systems.makefile import MakefileBuildSystem
from build_systems.edalize_integration import EdalizeIntegration


@pytest.fixture
def mock_config():
    return {
        "build_system": "makefile",
        "makefile_path": ".",
        "make_command": "make",
        "use_custom_makefile": True,
        "default_testbench": "my_testbench",
        "testbenches": {
            "my_testbench": {
                "tests": {
                    "basic_test": {"runtime_args": ["+UVM_TESTNAME=basic_test", "+TIMEOUT=1000"]},
                    "extended_test": {"runtime_args": ["+UVM_TESTNAME=extended_test", "+TIMEOUT=2000"]},
                }
            }
        },
    }


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def cleanup_dir():
    """Ensure we restore the original directory after each test."""
    original_dir = os.getcwd()
    yield
    os.chdir(original_dir)


class TestConfigFile:
    def test_find_config_file_specified(self, tmp_path):
        """Test finding a specified config file"""
        config_file = tmp_path / "my_config.yml"
        config_file.write_text("")

        result = find_config_file(str(config_file))
        assert result == str(config_file)

    def test_find_config_file_not_found_specified(self, tmp_path):
        """Test error when specified config file doesn't exist"""
        with pytest.raises(click.FileError) as exc_info:
            find_config_file(str(tmp_path / "nonexistent.yml"))
        assert "Configuration file not found" in str(exc_info.value)

    def test_find_config_file_default_tester_yml(self, tmp_path):
        """Test finding tester.yml by default"""
        original_dir = os.getcwd()
        os.chdir(tmp_path)
        config_file = tmp_path / "tester.yml"
        config_file.write_text("")

        try:
            result = find_config_file()
            assert os.path.abspath(result) == os.path.abspath(str(config_file))
        finally:
            os.chdir(original_dir)

    def test_find_config_file_default_config_yml(self, tmp_path):
        """Test finding config.yml when tester.yml doesn't exist"""
        original_dir = os.getcwd()
        os.chdir(tmp_path)
        config_file = tmp_path / "config.yml"
        config_file.write_text("")

        try:
            result = find_config_file()
            assert os.path.abspath(result) == os.path.abspath(str(config_file))
        finally:
            os.chdir(original_dir)

    def test_find_config_file_no_default(self, tmp_path):
        """Test error when no config file exists"""
        original_dir = os.getcwd()
        os.chdir(tmp_path)
        try:
            with pytest.raises(click.FileError) as exc_info:
                find_config_file()
            assert "No configuration file found" in str(exc_info.value)
        finally:
            os.chdir(original_dir)

    def test_load_config_invalid_yaml(self, tmp_path):
        """Test error when config file contains invalid YAML"""
        config_file = tmp_path / "config.yml"
        config_file.write_text("invalid: yaml: content:")

        with pytest.raises(click.FileError) as exc_info:
            load_config(str(config_file))
        assert "Invalid YAML format" in str(exc_info.value)

    def test_load_config_io_error(self, tmp_path):
        """Test error when config file can't be read"""
        config_file = tmp_path / "unreadable.yml"
        config_file.write_text("")
        config_file.chmod(0o000)  # Make file unreadable

        with pytest.raises(click.FileError) as exc_info:
            load_config(str(config_file))
        assert "Failed to load config" in str(exc_info.value)

    def test_load_config_empty(self, tmp_path):
        """Test loading empty config file"""
        config_file = tmp_path / "empty.yml"
        config_file.write_text("")

        config = load_config(str(config_file))
        assert config is None


class TestDefaultTestbench:
    def test_get_default_testbench_explicit(self, mock_config):
        """Test getting explicitly configured default testbench"""
        result = get_default_testbench(mock_config)
        assert result == "my_testbench"

    def test_get_default_testbench_first(self):
        """Test getting first testbench when no default is set"""
        config = {"template_config": {"testbenches": {"testbench1": {}, "testbench2": {}}}}
        result = get_default_testbench(config)
        assert result == "testbench1"

    def test_get_default_testbench_none(self):
        """Test error when no testbench can be found"""
        with pytest.raises(click.UsageError) as exc_info:
            get_default_testbench({})
        assert "No default testbench configured" in str(exc_info.value)


class TestCLICommands:
    @patch("cli.get_build_system")
    def test_list_testbenches(self, mock_get_build_system, cli_runner, mock_config):
        """Test listing testbenches"""
        mock_build_system = MagicMock()
        mock_build_system.get_available_testbenches.return_value = ["tb1", "tb2"]
        mock_get_build_system.return_value = mock_build_system

        result = cli_runner.invoke(cli, ["list-testbenches"], obj=mock_config)

        assert result.exit_code == 0
        assert "tb1" in result.output
        assert "tb2" in result.output

    @patch("cli.get_build_system")
    def test_list_tests(self, mock_get_build_system, cli_runner, mock_config):
        """Test listing tests for a testbench"""
        mock_build_system = MagicMock()
        mock_build_system.get_available_tests.return_value = ["test1", "test2"]
        mock_get_build_system.return_value = mock_build_system

        result = cli_runner.invoke(cli, ["list-tests", "my_testbench"], obj=mock_config)

        assert result.exit_code == 0
        assert "test1" in result.output
        assert "test2" in result.output

    @patch("cli.get_build_system")
    def test_build_testbench(self, mock_get_build_system, cli_runner, mock_config):
        """Test building a testbench"""
        mock_build_system = MagicMock()
        mock_build_system.build.return_value = True
        mock_get_build_system.return_value = mock_build_system

        result = cli_runner.invoke(cli, ["build", "my_testbench", "--debug"], obj=mock_config)

        assert result.exit_code == 0
        assert "Successfully built" in result.output
        mock_build_system.build.assert_called_once_with(
            "my_testbench", {"debug": True, "incremental": False, "verbose": False}
        )

    @patch("cli.get_build_system")
    def test_run_test(self, mock_get_build_system, cli_runner, mock_config):
        """Test running a test"""
        mock_build_system = MagicMock()
        mock_build_system.run.return_value = True
        mock_get_build_system.return_value = mock_build_system

        result = cli_runner.invoke(
            cli,
            [
                "run",
                "my_testbench",
                "basic_test",
                "--seed",
                "12345",
                "--verbosity",
                "HIGH",
                "--coverage",
                "--runtime-args",
                "+MY_ARG=value1",
            ],
            obj=mock_config,
        )

        assert result.exit_code == 0
        assert "Successfully ran test" in result.output

        # Verify the options passed to run
        call_args = mock_build_system.run.call_args[0]
        assert call_args[0] == "my_testbench"
        assert call_args[1] == "basic_test"

        options = call_args[2]
        assert options["seed"] == 12345
        assert options["verbosity"] == "HIGH"
        assert options["coverage"] is True
        assert "+MY_ARG=value1" in options["runtime_args"]

    @patch("cli.get_build_system")
    def test_clean_testbench(self, mock_get_build_system, cli_runner, mock_config):
        """Test cleaning a testbench"""
        mock_build_system = MagicMock()
        mock_build_system.clean.return_value = True
        mock_get_build_system.return_value = mock_build_system

        result = cli_runner.invoke(cli, ["clean", "my_testbench"], obj=mock_config)

        assert result.exit_code == 0
        assert "Successfully cleaned" in result.output
        mock_build_system.clean.assert_called_once_with("my_testbench")

    def test_default_testbench_commands(self, cli_runner, mock_config):
        """Test commands using default testbench"""
        with patch("cli.get_build_system") as mock_get_build_system:
            mock_build_system = MagicMock()
            mock_build_system.build.return_value = True
            mock_get_build_system.return_value = mock_build_system

            # Test build without specifying testbench
            result = cli_runner.invoke(cli, ["build"], obj=mock_config)
            assert result.exit_code == 0
            mock_build_system.build.assert_called_with(
                "my_testbench", {"debug": False, "incremental": False, "verbose": False}  # Should use default testbench
            )

    def test_list_testbenches_error(self, cli_runner, mock_config):
        """Test error handling in list-testbenches command"""
        with patch("cli.get_build_system") as mock_get_build_system, patch(
            "cli.logger"
        ) as mock_logger:  # Patch the logger directly
            mock_build_system = MagicMock()
            mock_build_system.get_available_testbenches.side_effect = Exception("Test error")
            mock_get_build_system.return_value = mock_build_system

            # Capture stderr to check error message
            result = cli_runner.invoke(cli, ["list-testbenches"], obj=mock_config, catch_exceptions=False)
            assert result.exit_code != 0
            # Verify the error was logged
            mock_logger.error.assert_called_once_with("Failed to list testbenches: Test error")

    def test_list_tests_no_tests(self, cli_runner, mock_config):
        """Test list-tests when no tests are found"""
        with patch("cli.get_build_system") as mock_get_build_system:
            mock_build_system = MagicMock()
            mock_build_system.get_available_tests.return_value = []
            mock_get_build_system.return_value = mock_build_system

            result = cli_runner.invoke(cli, ["list-tests", "my_testbench"], obj=mock_config)
            assert "No tests found" in result.output

    def test_build_failure(self, cli_runner, mock_config):
        """Test build command failure"""
        with patch("cli.get_build_system") as mock_get_build_system:
            mock_build_system = MagicMock()
            mock_build_system.build.return_value = False
            mock_get_build_system.return_value = mock_build_system

            result = cli_runner.invoke(cli, ["build", "my_testbench"], obj=mock_config)
            assert result.exit_code != 0
            assert "Failed to build testbench" in result.output

    def test_run_test_failure(self, cli_runner, mock_config):
        """Test run command failure"""
        with patch("cli.get_build_system") as mock_get_build_system:
            mock_build_system = MagicMock()
            mock_build_system.run.return_value = False
            mock_get_build_system.return_value = mock_build_system

            result = cli_runner.invoke(cli, ["run", "my_testbench", "basic_test"], obj=mock_config)
            assert result.exit_code != 0
            assert "Failed to run test" in result.output

    def test_clean_failure(self, cli_runner, mock_config):
        """Test clean command failure"""
        with patch("cli.get_build_system") as mock_get_build_system:
            mock_build_system = MagicMock()
            mock_build_system.clean.return_value = False
            mock_get_build_system.return_value = mock_build_system

            result = cli_runner.invoke(cli, ["clean", "my_testbench"], obj=mock_config)
            assert result.exit_code != 0
            assert "Failed to clean testbench" in result.output

    def test_cli_verbose_option(self, cli_runner):
        """Test verbose option sets correct log level"""
        with patch("logging.basicConfig") as mock_logging:
            cli_runner.invoke(cli, ["--verbose", "list-testbenches"])
            mock_logging.assert_called_once_with(level=logging.DEBUG)

    def test_cli_config_load_error(self, cli_runner, tmp_path):
        """Test CLI handles config loading errors"""
        config_file = tmp_path / "bad_config.yml"
        config_file.write_text("invalid: yaml: :")

        result = cli_runner.invoke(cli, ["--config", str(config_file), "list-testbenches"], catch_exceptions=False)
        assert result.exit_code != 0
        # Check stderr for error message
        with patch("cli.logger") as mock_logger:
            cli_runner.invoke(cli, ["--config", str(config_file), "list-testbenches"])
            mock_logger.error.assert_called_with(
                "Invalid YAML format: mapping values are not allowed here\n" '  in "{}", line 1, column 14'.format(config_file)
            )

    def test_list_tests_with_no_testbench_and_no_default(self, cli_runner):
        """Test list-tests fails gracefully when no testbench is specified or found"""
        config = {}  # Empty config, no default testbench
        with patch("cli.get_default_testbench") as mock_get_default, patch("cli.logger") as mock_logger:
            mock_get_default.side_effect = click.UsageError("No default testbench configured")
            result = cli_runner.invoke(cli, ["list-tests"], obj=config)

            assert result.exit_code != 0
            mock_logger.error.assert_called_with("Failed to list tests: No default testbench configured")

    def test_run_test_with_invalid_verbosity(self, cli_runner, mock_config):
        """Test run command with invalid verbosity level"""
        result = cli_runner.invoke(cli, ["run", "my_testbench", "basic_test", "--verbosity", "INVALID"], obj=mock_config)
        assert result.exit_code != 0
        assert "Invalid value for '--verbosity'" in result.output

    def test_list_tests_error(self, cli_runner, mock_config):
        """Test error handling in list-tests command"""
        with patch("cli.get_build_system") as mock_get_build_system, patch("cli.logger") as mock_logger:
            mock_build_system = MagicMock()
            mock_build_system.get_available_tests.side_effect = Exception("Test error")
            mock_get_build_system.return_value = mock_build_system

            result = cli_runner.invoke(cli, ["list-tests", "my_testbench"], obj=mock_config, catch_exceptions=False)
            assert result.exit_code != 0
            mock_logger.error.assert_called_once_with("Failed to list tests: Test error")


class TestBuildSystem:
    def test_get_build_system_makefile(self, mock_config):
        """Test getting makefile build system"""
        with patch("cli.MakefileBuildSystem") as mock_makefile:
            mock_instance = MagicMock()
            mock_makefile.return_value = mock_instance

            build_system = get_build_system(mock_config)
            assert build_system == mock_instance
            mock_makefile.assert_called_once_with(mock_config)

    def test_get_build_system_edalize(self):
        """Test getting edalize build system"""
        config = {"build_system": "edalize"}
        with patch("cli.EdalizeIntegration") as mock_edalize:
            mock_instance = MagicMock()
            mock_edalize.return_value = mock_instance

            build_system = get_build_system(config)
            assert build_system == mock_instance
            mock_edalize.assert_called_once_with(config)

    def test_get_build_system_unsupported(self):
        """Test error on unsupported build system"""
        config = {"build_system": "unsupported"}
        with pytest.raises(ValueError) as exc_info:
            get_build_system(config)
        assert "Unsupported build system" in str(exc_info.value)

    def test_get_build_system_default(self):
        """Test getting default (makefile) build system when not specified"""
        config = {}  # No build system specified
        with patch("cli.MakefileBuildSystem") as mock_makefile:
            mock_instance = MagicMock()
            mock_makefile.return_value = mock_instance

            build_system = get_build_system(config)
            assert build_system == mock_instance
            mock_makefile.assert_called_once_with(config)
