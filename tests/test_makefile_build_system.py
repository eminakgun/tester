import pytest
from unittest.mock import patch, MagicMock
import subprocess

from build_systems.makefile import MakefileBuildSystem


@pytest.fixture
def makefile_config():
    return {
        "makefile_path": "/path/to/makefile",
        "make_command": "make"
    }


@pytest.fixture
def makefile_system(makefile_config):
    return MakefileBuildSystem(makefile_config)


def test_init(makefile_system, makefile_config):
    assert makefile_system.makefile_path == makefile_config["makefile_path"]
    assert makefile_system.make_command == makefile_config["make_command"]


@patch('subprocess.run')
def test_build_success(mock_run, makefile_system):
    mock_run.return_value = MagicMock(returncode=0)
    
    result = makefile_system.build("my_testbench", {"SIMULATOR": "vcs"})
    
    mock_run.assert_called_once()
    cmd_args = mock_run.call_args[0][0]
    assert "build" in cmd_args
    assert "TESTBENCH=my_testbench" in cmd_args
    assert "SIMULATOR=vcs" in cmd_args
    assert result is True


@patch('subprocess.run')
def test_build_failure(mock_run, makefile_system):
    # Create the exception correctly for Python 3.13
    error = subprocess.CalledProcessError(1, [])
    error.stdout = b''
    error.stderr = b'Error'
    mock_run.side_effect = error
    
    result = makefile_system.build("my_testbench")
    
    mock_run.assert_called_once()
    assert result is False


@patch('subprocess.run')
def test_run_success(mock_run, makefile_system):
    mock_run.return_value = MagicMock(returncode=0)
    
    result = makefile_system.run("my_testbench", "basic_test", {"SEED": "123"})
    
    mock_run.assert_called_once()
    cmd_args = mock_run.call_args[0][0]
    assert "run" in cmd_args
    assert "TESTBENCH=my_testbench" in cmd_args
    assert "TEST=basic_test" in cmd_args
    assert "SEED=123" in cmd_args
    assert result is True


@patch('subprocess.run')
def test_clean_success(mock_run, makefile_system):
    mock_run.return_value = MagicMock(returncode=0)
    
    result = makefile_system.clean("my_testbench")
    
    mock_run.assert_called_once()
    cmd_args = mock_run.call_args[0][0]
    assert "clean" in cmd_args
    assert "TESTBENCH=my_testbench" in cmd_args
    assert result is True


@patch('subprocess.run')
def test_get_available_testbenches(mock_run, makefile_system):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=b'testbench1\ntestbench2\ntestbench3\n'
    )
    
    result = makefile_system.get_available_testbenches()
    
    mock_run.assert_called_once()
    cmd_args = mock_run.call_args[0][0]
    assert "list-testbenches" in cmd_args
    assert result == ["testbench1", "testbench2", "testbench3"]


@patch('subprocess.run')
def test_get_available_tests(mock_run, makefile_system):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=b'test1\ntest2\ntest3\n'
    )
    
    result = makefile_system.get_available_tests("my_testbench")
    
    mock_run.assert_called_once()
    cmd_args = mock_run.call_args[0][0]
    assert "list-tests" in cmd_args
    assert "TESTBENCH=my_testbench" in cmd_args
    assert result == ["test1", "test2", "test3"] 