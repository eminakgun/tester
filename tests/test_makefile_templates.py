import os
import pytest
from unittest.mock import patch, mock_open, MagicMock

from build_systems.makefile.templates import MakefileTemplate, UVMTestbenchMakefile, MakefileTemplateFactory


class TestMakefileTemplate:
    def test_init(self):
        config = {"output_dir": "/tmp/output"}
        template = MakefileTemplate(config)

        assert template.config == config
        assert template.output_dir == "/tmp/output"

    def test_generate_abstract(self):
        config = {}
        template = MakefileTemplate(config)

        with pytest.raises(NotImplementedError):
            template.generate()


class TestUVMTestbenchMakefile:
    @pytest.fixture
    def basic_config(self):
        return {
            "simulator": "vcs",
            "includes": ["+incdir+./include", "+incdir+./src"],
            "defines": {"TEST_DEFINE": "1", "SIMULATOR_VCS": ""},
            "src_files": ["./src/file1.sv", "./src/file2.sv"],
            "tb_files": ["./tb/tb_top.sv", "./tb/tests.sv"],
            "testbenches": {"tb1": {"tests": ["test1", "test2"]}, "tb2": {"tests": ["test3", "test4"]}},
            "build_options": {},
            "run_options": {},
        }

    def test_generate_content_basic(self, basic_config):
        template = UVMTestbenchMakefile(basic_config)
        content = template._generate_content()

        # Check for basic elements
        assert "# Generated UVM Testbench Makefile" in content
        assert "SIMULATOR ?= vcs" in content

        # Check for includes
        assert "+incdir+./include" in content
        assert "+incdir+./src" in content

        # Check for defines
        assert "+define+TEST_DEFINE=1" in content
        assert "+define+SIMULATOR_VCS" in content

        # Check for source files
        assert "SRC_FILES += ./src/file1.sv" in content
        assert "SRC_FILES += ./src/file2.sv" in content
        assert "TB_FILES += ./tb/tb_top.sv" in content
        assert "TB_FILES += ./tb/tests.sv" in content

        # Check for VCS section
        assert "# VCS-specific settings" in content
        assert "ifeq ($(SIMULATOR),vcs)" in content
        assert "BUILD_CMD = $(VCS)" in content

        # Check for common targets
        assert ".PHONY: all build run clean help list-testbenches list-tests" in content
        assert "build:" in content
        assert "run:" in content
        assert "clean:" in content

        # Check for testbench listing
        assert "list-testbenches:" in content
        assert '@echo "tb1"' in content
        assert '@echo "tb2"' in content

        # Check for test listing
        assert "list-tests:" in content
        assert 'case "$(TESTBENCH)" in' in content
        assert "tb1)" in content
        assert 'echo "test1"' in content
        assert 'echo "test2"' in content
        assert "tb2)" in content
        assert 'echo "test3"' in content
        assert 'echo "test4"' in content

    def test_vcs_settings(self, basic_config):
        template = UVMTestbenchMakefile(basic_config)
        content = template._generate_content()

        # Check VCS settings
        assert "VCS_HOME ?= $(VCS_HOME)" in content
        assert "VCS = $(VCS_HOME)/bin/vcs" in content
        assert "-full64 -sverilog -timescale=1ns/1ps -CFLAGS -DVCS" in content
        assert "-debug_access+all" in content
        assert "-cm line+cond+fsm+branch+tgl" in content

    def test_questa_specific_settings(self):
        config = {
            "simulator": "questa",
            "includes": [],
            "defines": {},
            "src_files": [],
            "tb_files": [],
            "testbenches": {},
            "build_options": {"questa_home": "/opt/questa", "debug": True, "coverage": True},
            "run_options": {},
        }

        template = UVMTestbenchMakefile(config)
        content = template._generate_content()

        # Check Questa settings
        assert "QUESTA_HOME ?= /opt/questa" in content
        assert "VLOG = $(QUESTA_HOME)/bin/vlog" in content
        assert "VSIM = $(QUESTA_HOME)/bin/vsim" in content
        assert "-debugdb" in content
        assert "+cover=bcestf" in content

    def test_xcelium_specific_settings(self):
        config = {
            "simulator": "xcelium",
            "includes": [],
            "defines": {},
            "src_files": [],
            "tb_files": [],
            "testbenches": {},
            "build_options": {"xcelium_home": "/opt/xcelium", "debug": False, "coverage": False},
            "run_options": {},
        }

        template = UVMTestbenchMakefile(config)
        content = template._generate_content()

        # Check Xcelium settings
        assert "XCELIUM_HOME ?= /opt/xcelium" in content
        assert "XRUN = $(XCELIUM_HOME)/bin/xrun" in content
        assert "-debug" not in content  # debug is disabled
        assert "-coverage all" not in content  # coverage is disabled


class TestMakefileTemplateFactory:
    def test_create_uvm_template(self):
        config = {"simulator": "vcs"}
        template = MakefileTemplateFactory.create("uvm", config)

        assert isinstance(template, UVMTestbenchMakefile)

    def test_create_invalid_template(self):
        config = {}

        with pytest.raises(ValueError):
            MakefileTemplateFactory.create("invalid", config)


class TestMakefileTemplateFileOutput:
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_generate_with_output_path(self, mock_file, mock_makedirs):
        config = {"simulator": "vcs"}
        template = UVMTestbenchMakefile(config)

        # Mock _generate_content to return a simple string
        template._generate_content = MagicMock(return_value="Makefile content")

        template.generate("/path/to/Makefile")

        mock_makedirs.assert_called_once_with("/path/to", exist_ok=True)
        mock_file.assert_called_once_with("/path/to/Makefile", "w")
        mock_file().write.assert_called_once_with("Makefile content")
