# Riviera-Pro specific settings
VSIM = vsim
VLOG = vlog
VSIMFLAGS = -c -do "run -all; exit;"

# Common source files and directories
RTL_DIR = rtl
TB_DIR = tb
BUILD_DIR = build
RESULTS_DIR = results

RTL_SRCS = $(wildcard $(RTL_DIR)/*.v)
TB_SRCS = $(wildcard $(TB_DIR)/*.sv)

# Default variables
TEST ?= basic_test
RUNTIME_ARGS ?=

# Testbench targets
.PHONY: all build_all sim_all clean
.PHONY: build_testbench1 build_testbench2 sim_testbench1 sim_testbench2
.PHONY: list-testbenches list-tests

# Main targets
all: build_all sim_all

build_all: build_testbench1 build_testbench2

sim_all: sim_testbench1 sim_testbench2

# Build targets
build_testbench1: $(RTL_SRCS) $(TB_DIR)/testbench1.sv
	@mkdir -p $(BUILD_DIR)/testbench1
	cd $(BUILD_DIR)/testbench1 && $(VLOG) -work work ../../$(RTL_DIR)/*.v ../../$(TB_DIR)/testbench1.sv

build_testbench2: $(RTL_SRCS) $(TB_DIR)/testbench2.sv
	@mkdir -p $(BUILD_DIR)/testbench2
	cd $(BUILD_DIR)/testbench2 && $(VLOG) -work work ../../$(RTL_DIR)/*.v ../../$(TB_DIR)/testbench2.sv

# Simulation targets (removed build dependencies)
sim_testbench1:
	@mkdir -p $(RESULTS_DIR)/testbench1
	cd $(BUILD_DIR)/testbench1 && $(VSIM) $(VSIMFLAGS) \
		-l ../../$(RESULTS_DIR)/testbench1/$(TEST).log \
		work.testbench1 $(RUNTIME_ARGS)

sim_testbench2: build_testbench2
	@mkdir -p $(RESULTS_DIR)/testbench2
	cd $(BUILD_DIR)/testbench2 && $(VSIM) $(VSIMFLAGS) \
		-l ../../$(RESULTS_DIR)/testbench2/$(TEST).log \
		work.testbench2 $(RUNTIME_ARGS)

# Utility targets
clean:
	rm -rf $(BUILD_DIR) $(RESULTS_DIR) work transcript vsim.wlf

list-testbenches:
	@echo "testbench1"
	@echo "testbench2"

list-tests:
	@case "$(TESTBENCH)" in \
		testbench1) \
			echo "basic_test"; \
			echo "extended_test";; \
		testbench2) \
			echo "sanity_test"; \
			echo "regression_test";; \
		*) \
			echo "Unknown testbench: $(TESTBENCH)"; \
			exit 1;; \
	esac 