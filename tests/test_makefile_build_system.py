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


@pytest.fixture
def config_with_separate_commands():
    return {
        "makefile_path": ".",
        "make_command": "make",
        "targets": {
            "testbench1": {
                "build_command": "make build_testbench1",
                "run_command": "make sim_testbench1"
            }
        }
    }


@pytest.fixture
def config_with_combined_command():
    return {
        "makefile_path": ".",
        "make_command": "make",
        "targets": {
            "testbench2": {
                "run_command": "make sim_testbench2"
            }
        }
    }


class TestMakefileBuildSystem:
    @patch('subprocess.run')
    def test_run_with_separate_build_command(self, mock_run, config_with_separate_commands):
        """Test run when testbench has separate build command"""
        # Setup
        mock_run.return_value = MagicMock(returncode=0)
        build_system = MakefileBuildSystem(config_with_separate_commands)
        
        # Execute
        result = build_system.run("testbench1", "basic_test", {"SIMULATOR": "vcs"})
        
        # Verify
        assert mock_run.call_count == 2  # Should call both build and run
        
        # Verify build call
        build_call = mock_run.call_args_list[0]
        assert "build_testbench1" in build_call[0][0]  # Check for custom build target
        assert "TESTBENCH=testbench1" in build_call[0][0]
        
        # Verify run call
        run_call = mock_run.call_args_list[1]
        assert "sim_testbench1" in run_call[0][0]  # Check for custom run target
        assert "TESTBENCH=testbench1" in run_call[0][0]
        assert "TEST=basic_test" in run_call[0][0]
        
        assert result is True

    @patch('subprocess.run')
    def test_run_with_combined_command(self, mock_run, config_with_combined_command):
        """Test run when testbench has only run command"""
        # Setup
        mock_run.return_value = MagicMock(returncode=0)
        build_system = MakefileBuildSystem(config_with_combined_command)
        
        # Execute
        result = build_system.run("testbench2", "basic_test", {"SIMULATOR": "vcs"})
        
        # Verify
        mock_run.assert_called_once()  # Should only call run once
        cmd_args = mock_run.call_args[0][0]
        assert "sim_testbench2" in cmd_args  # Check for custom run target
        assert "TESTBENCH=testbench2" in cmd_args
        assert "TEST=basic_test" in cmd_args
        assert result is True

    @patch('subprocess.run')
    def test_run_with_build_failure(self, mock_run, config_with_separate_commands):
        """Test run when build fails"""
        # Setup
        error = subprocess.CalledProcessError(1, [])
        error.stdout = b'Build failed'
        error.stderr = b'Error during build'
        mock_run.side_effect = error
        
        build_system = MakefileBuildSystem(config_with_separate_commands)
        
        # Execute
        result = build_system.run("testbench1", "basic_test")
        
        # Verify
        mock_run.assert_called_once()  # Should only try to build
        cmd_args = mock_run.call_args[0][0]
        assert "build_testbench1" in cmd_args  # Check for custom build target
        assert result is False  # Should fail due to build failure

    @patch('subprocess.run')
    def test_run_with_runtime_args(self, mock_run, config_with_separate_commands):
        """Test run with runtime arguments"""
        # Setup
        mock_run.return_value = MagicMock(returncode=0)
        build_system = MakefileBuildSystem(config_with_separate_commands)
        
        options = {
            "runtime_args": ["+UVM_TESTNAME=test1", "+TIMEOUT=1000"],
            "seed": 12345,
            "verbosity": "high"
        }
        
        # Execute
        result = build_system.run("testbench1", "basic_test", options)
        
        # Verify
        assert mock_run.call_count == 2
        run_call = mock_run.call_args_list[1]
        cmd_args = run_call[0][0]
        assert "RUNTIME_ARGS=+UVM_TESTNAME=test1 +TIMEOUT=1000" in cmd_args
        assert "SEED=12345" in cmd_args
        assert "VERBOSITY=UVM_HIGH" in cmd_args
        assert result is True


@patch('subprocess.run')
def test_build_with_custom_build_command(mock_run, makefile_config):
    """Test build when testbench has a custom build command"""
    # Setup
    config = makefile_config.copy()
    config["targets"] = {
        "custom_testbench": {
            "build_command": "make custom_build_target",
            "run_command": "make custom_run_target"
        }
    }
    
    mock_run.return_value = MagicMock(returncode=0)
    build_system = MakefileBuildSystem(config)
    
    # Execute
    result = build_system.build("custom_testbench", {"debug": True})
    
    # Verify
    mock_run.assert_called_once()
    cmd_args = mock_run.call_args[0][0]
    
    # Verify the custom target is used instead of the default "build" target
    assert "custom_build_target" in cmd_args
    assert "build" not in cmd_args
    assert "TESTBENCH=custom_testbench" in cmd_args
    assert "DEBUG=1" in cmd_args
    assert result is True


@patch('subprocess.run')
def test_run_with_custom_run_command(mock_run, makefile_config):
    """Test run when testbench has a custom run command"""
    # Setup
    config = makefile_config.copy()
    config["targets"] = {
        "custom_testbench": {
            "build_command": "make custom_build_target",
            "run_command": "make custom_run_target"
        }
    }
    
    mock_run.return_value = MagicMock(returncode=0)
    build_system = MakefileBuildSystem(config)
    
    # Execute - first mock the build method to isolate testing of run
    with patch.object(build_system, 'build', return_value=True):
        result = build_system.run("custom_testbench", "test_case", {"debug": True})
    
    # Verify
    mock_run.assert_called_once()
    cmd_args = mock_run.call_args[0][0]
    
    # Verify the custom target is used instead of the default "run" target
    assert "custom_run_target" in cmd_args
    assert "run" not in cmd_args
    assert "TESTBENCH=custom_testbench" in cmd_args
    assert "TEST=test_case" in cmd_args
    assert "DEBUG=1" in cmd_args
    assert result is True 