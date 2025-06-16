import importlib
import os
import shutil
from unittest.mock import MagicMock, mock_open, patch

import pytest

from build_systems.edalize_integration import EdalizeIntegration


@pytest.fixture
def edalize_config():
    return {
        "work_root": "/tmp/edalize_test",
        "tool": "vcs",
        "parameters": {"PARAM1": "value1"},
        "files": [
            {"name": "src/file1.sv", "file_type": "systemVerilogSource"},
            {"name": "src/file2.sv", "file_type": "systemVerilogSource"},
        ],
        "testbenches": {
            "testbench1": {
                "toplevel": "tb_top",
                "files": [{"name": "tb/tb_top.sv", "file_type": "systemVerilogSource"}],
                "parameters": {"TB_PARAM": "tb_value"},
                "tests": {"test1": {"PARAM2": "test1_value"}, "test2": {"PARAM2": "test2_value"}},
            }
        },
        "vcs_options": {"compile_flags": ["-sverilog", "-full64"]},
    }


@pytest.fixture
def edalize_system(edalize_config):
    return EdalizeIntegration(edalize_config)


def test_init(edalize_system, edalize_config):
    assert edalize_system.work_root == edalize_config["work_root"]
    assert edalize_system.tool == edalize_config["tool"]
    assert edalize_system.parameters == edalize_config["parameters"]
    assert edalize_system.files == edalize_config["files"]
    assert edalize_system.testbenches == edalize_config["testbenches"]
    assert edalize_system.tool_options["vcs"] == edalize_config["vcs_options"]


def test_prepare_edalize_config(edalize_system):
    # Test basic config
    config = edalize_system._prepare_edalize_config("testbench1")

    assert config["name"] == "testbench1"
    assert config["toplevel"] == "tb_top"
    assert len(config["files"]) == 3  # 2 base files + 1 testbench file
    assert config["parameters"]["PARAM1"] == "value1"
    assert config["parameters"]["TB_PARAM"] == "tb_value"
    assert config["tool_options"]["vcs"]["compile_flags"] == ["-sverilog", "-full64"]

    # Test with test
    config = edalize_system._prepare_edalize_config("testbench1", "test1")

    assert config["parameters"]["PARAM1"] == "value1"
    assert config["parameters"]["TB_PARAM"] == "tb_value"
    assert config["parameters"]["PARAM2"] == "test1_value"
    assert config["parameters"]["uvm_testname"] == "test1"


@patch("importlib.import_module")
@patch("os.makedirs")
def test_get_edalize_backend(mock_makedirs, mock_import, edalize_system):
    """Test the _get_edalize_backend method."""
    # Setup mock module and class
    mock_module = MagicMock()
    mock_class = MagicMock()
    mock_backend = MagicMock()

    # Configure mocks
    mock_module.Vcs = mock_class
    mock_class.return_value = mock_backend
    mock_import.return_value = mock_module

    # Explicitly ensure makedirs doesn't raise any exception
    mock_makedirs.return_value = None

    # Call the method
    backend = edalize_system._get_edalize_backend("testbench1")

    # Check that makedirs was called at least once
    assert mock_makedirs.call_count >= 1

    # Check if any of the calls match our expected arguments
    expected_path = os.path.join(edalize_system.work_root, "testbench1")
    expected_args_found = False

    for call in mock_makedirs.call_args_list:
        args, kwargs = call
        if args[0] == expected_path and kwargs.get("exist_ok", False):
            expected_args_found = True
            break

    assert expected_args_found, f"makedirs was not called with expected path: {expected_path}"
    mock_import.assert_called_once_with("edalize.vcs")
    assert backend == mock_backend


@patch("importlib.import_module")
@patch("os.makedirs")
@patch("os.path.exists")
def test_build_success(mock_exists, mock_makedirs, mock_import, edalize_system):
    # Setup mock module and class
    mock_module = MagicMock()
    mock_class = MagicMock()
    mock_backend = MagicMock()

    mock_module.Vcs = mock_class
    mock_class.return_value = mock_backend
    mock_import.return_value = mock_module
    mock_exists.return_value = False

    # Call method
    result = edalize_system.build("testbench1", {"debug": True})

    # Verify
    mock_backend.configure.assert_called_once()
    mock_backend.build.assert_called_once()
    assert result is True


@patch("importlib.import_module")
@patch("os.makedirs")
@patch("os.path.exists")
def test_build_failure(mock_exists, mock_makedirs, mock_import, edalize_system):
    # Setup mock module and class
    mock_module = MagicMock()
    mock_class = MagicMock()
    mock_backend = MagicMock()

    mock_module.Vcs = mock_class
    mock_class.return_value = mock_backend
    mock_import.return_value = mock_module
    mock_exists.return_value = False

    # Make build fail
    mock_backend.build.side_effect = Exception("Build failed")

    # Call method
    result = edalize_system.build("testbench1")

    # Verify
    mock_backend.configure.assert_called_once()
    mock_backend.build.assert_called_once()
    assert result is False


@patch("importlib.import_module")
@patch("os.makedirs")
@patch("os.path.exists")
def test_run_success(mock_exists, mock_makedirs, mock_import, edalize_system):
    # Setup mock module and class
    mock_module = MagicMock()
    mock_class = MagicMock()
    mock_backend = MagicMock()

    mock_module.Vcs = mock_class
    mock_class.return_value = mock_backend
    mock_import.return_value = mock_module
    mock_exists.return_value = True  # Makefile exists

    # Call method
    result = edalize_system.run("testbench1", "test1", {"seed": 12345, "verbosity": "high"})

    # Verify
    mock_backend.configure.assert_not_called()
    mock_backend.run.assert_called_once()

    # Check run options
    run_options = mock_backend.run.call_args[0][0]
    assert run_options["ntb_random_seed"] == "12345"
    assert run_options["UVM_VERBOSITY"] == "UVM_HIGH"
    assert result is True


@patch("shutil.rmtree")
@patch("os.path.exists")
def test_clean_success(mock_exists, mock_rmtree, edalize_system):
    mock_exists.return_value = True

    result = edalize_system.clean("testbench1")

    mock_rmtree.assert_called_once_with(os.path.join(edalize_system.work_root, "testbench1"))
    assert result is True


def test_get_available_testbenches(edalize_system):
    testbenches = edalize_system.get_available_testbenches()

    assert testbenches == ["testbench1"]


def test_get_available_tests(edalize_system):
    tests = edalize_system.get_available_tests("testbench1")

    assert sorted(tests) == ["test1", "test2"]

    # Test with unknown testbench
    tests = edalize_system.get_available_tests("unknown")

    assert tests == []
