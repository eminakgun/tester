# Generated UVM Testbench Makefile
# Do not edit manually

# Default variables
SIMULATOR ?= vcs
TESTBENCH ?= $(error TESTBENCH is not set)
TEST ?= $(error TEST is not set)
SEED ?= random
DEBUG ?= 0
COVERAGE ?= 0
VERBOSITY ?= UVM_MEDIUM

# Directory structure
SIM_DIR ?= ./sim
BUILD_DIR ?= $(SIM_DIR)/build/$(TESTBENCH)
RESULTS_DIR ?= $(SIM_DIR)/results/$(TESTBENCH)/$(TEST)

# Include paths

# Define macros

# Source files

# Testbench files

# VCS-specific settings
ifeq ($(SIMULATOR),vcs)
  VCS_HOME ?= $(VCS_HOME)
  VCS = $(VCS_HOME)/bin/vcs
  SIMV = $(BUILD_DIR)/simv

  # Debug settings
  ifeq ($(DEBUG),1)
    DEBUG_ARGS = -debug_access+all
  else
    DEBUG_ARGS =
  endif

  # Coverage settings
  ifeq ($(COVERAGE),1)
    COVERAGE_ARGS = -cm line+cond+fsm+branch+tgl
  else
    COVERAGE_ARGS =
  endif

  # Build command
  BUILD_CMD = $(VCS) -o $(SIMV) $(SRC_FILES) $(TB_FILES) \
              $(INCLUDE_DIRS) $(DEFINES) \
              -full64 -sverilog -timescale=1ns/1ps -CFLAGS -DVCS \
              $(DEBUG_ARGS) $(COVERAGE_ARGS) \
              -ntb_opts uvm-1.2

  # Run command
  RUN_CMD = $(SIMV) -l $(RESULTS_DIR)/sim.log \
            +UVM_TESTNAME=$(TEST) \
            +UVM_VERBOSITY=$(VERBOSITY) \
            +ntb_random_seed=$(SEED) \
            $(if $(COVERAGE),,-cm_dir $(RESULTS_DIR)/coverage)
endif

# Common targets
.PHONY: all build run clean help list-testbenches list-tests

all: build run

build:
	@mkdir -p $(BUILD_DIR)
	$(BUILD_CMD)

run:
	@mkdir -p $(RESULTS_DIR)
	$(RUN_CMD)

clean:
	rm -rf $(BUILD_DIR)

help:
	@echo "UVM Testbench Makefile"
	@echo "Usage:"
	@echo "  make build TESTBENCH=<testbench>"
	@echo "  make run TESTBENCH=<testbench> TEST=<test> [SEED=<seed>] [DEBUG=0|1] [COVERAGE=0|1]"
	@echo "  make clean TESTBENCH=<testbench>"
	@echo "  make list-testbenches"
	@echo "  make list-tests TESTBENCH=<testbench>"

list-testbenches:
	@echo "my_testbench"

list-tests:
	@case "$(TESTBENCH)" in \
		my_testbench) \
			echo "basic_test"; \
			echo "extended_test"; \
			;; \
		*) \
			echo "Unknown testbench: $(TESTBENCH)"; \
			exit 1; \
			;; \
	esac