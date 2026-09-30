# Makefile for Tiny Tapeout Cocotb Simulation
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
SRC_DIR = $(PWD)/../src

PROJECT_SOURCES = \
    tt_um_ares_sentinel_project.v \
    ares_sentinel_top.v \
    ares_timing_sentinel.v \
    ares_frame_fsm.v \
    ares_fault_arbiter.v \
    ares_fault_latch.v \
    ares_isolation_gate.v \
    ares_isolation_l3.v \
    edge_detect.v \
    state_machine.v \
    data_multiplex.v \
    serial_decode.v \
    data_validate.v

COMPILE_ARGS += -g2012 -I$(SRC_DIR)

ifneq ($(GATES),yes)
VERILOG_SOURCES = $(addprefix $(SRC_DIR)/, $(PROJECT_SOURCES))
else
VERILOG_SOURCES = $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v \
                  $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v \
                  $(PWD)/../runs/wokwi/results/final/verilog/gl/tt_um_ares_sentinel_project.v
COMPILE_ARGS += -DGL_TEST
endif

VERILOG_SOURCES += $(PWD)/tb.v
TOPLEVEL = tb
MODULE = test

include $(shell cocotb-config --makefiles)/Makefile.sim
