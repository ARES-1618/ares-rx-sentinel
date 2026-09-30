# ==============================================================================
# ARES-RX Sentinel — OpenLane Dual-Mode Configuration Script
# Architecture: Tiny Tapeout TT08 & Chip Merah Putih Sandbox Flow
# Process: SkyWater 130nm (sky130_fd_sc_hd)
# Tile Size: TT08 1x1 Standard Tile (0 0 161.00 111.52)
# ==============================================================================

# Common user-tunable synthesis & implementation variables
set ::env(PL_TARGET_DENSITY) 0.65
set ::env(CLOCK_PERIOD) "20"
set ::env(PL_RESIZER_HOLD_SLACK_MARGIN) 0.1
set ::env(GLB_RESIZER_HOLD_SLACK_MARGIN) 0.05
set ::env(RUN_LINTER) 1
set ::env(LINTER_INCLUDE_PDK_MODELS) 1
set ::env(CLOCK_PORT) {clk}

set script_dir [file dirname [file normalize [info script]]]

# Dual-Mode Branching:
# Mode A: Tiny Tapeout CI Flow (auto-generated user_config.tcl present)
# Mode B: Chip Merah Putih Sandbox Flow (standalone OpenLane hardening)
if {[info exists ::env(DESIGN_DIR)] && [file exists $::env(DESIGN_DIR)/user_config.tcl]} {
    source $::env(DESIGN_DIR)/user_config.tcl
} else {
    # Standalone OpenLane / Chip Merah Putih Sandbox Configuration
    set ::env(DESIGN_NAME) "tt_um_ares_sentinel_project"
    set ::env(VERILOG_FILES) "\
        $script_dir/tt_um_ares_sentinel_project.v \
        $script_dir/ares_sentinel_top.v \
        $script_dir/ares_timing_sentinel.v \
        $script_dir/ares_frame_fsm.v \
        $script_dir/ares_fault_arbiter.v \
        $script_dir/ares_fault_latch.v \
        $script_dir/ares_isolation_gate.v \
        $script_dir/ares_isolation_l3.v \
        $script_dir/edge_detect.v \
        $script_dir/state_machine.v \
        $script_dir/data_multiplex.v \
        $script_dir/serial_decode.v \
        $script_dir/data_validate.v"

    set ::env(PDK) "sky130A"
    set ::env(STD_CELL_LIBRARY) "sky130_fd_sc_hd"

    # Absolute die size for TT08 1x1 tile (161.00 um x 111.52 um)
    set ::env(DIE_AREA) "0 0 161.00 111.52"
    set ::env(FP_SIZING) absolute
}

# OpenLane TT08 Hardening & Routing Constraints
set ::env(RUN_KLAYOUT_XOR) 0
set ::env(RUN_KLAYOUT_DRC) 0
set ::env(PL_RESIZER_BUFFER_OUTPUT_PORTS) 0
set ::env(SYNTH_READ_BLACKBOX_LIB) 1

# Placement Margins
set ::env(TOP_MARGIN_MULT) 1
set ::env(BOTTOM_MARGIN_MULT) 1
set ::env(LEFT_MARGIN_MULT) 6
set ::env(RIGHT_MARGIN_MULT) 6

set ::env(PL_BASIC_PLACEMENT) {0}
set ::env(GRT_ALLOW_CONGESTION) "1"
set ::env(FP_IO_HLENGTH) 2
set ::env(FP_IO_VLENGTH) 2

# Decap Cells for SkyWater 130nm
set ::env(DECAP_CELL) "\
    sky130_fd_sc_hd__decap_3 \
    sky130_fd_sc_hd__decap_4 \
    sky130_fd_sc_hd__decap_6 \
    sky130_fd_sc_hd__decap_8 \
    sky130_ef_sc_hd__decap_12"

# Clock Tree Synthesis & Routing Layer Caps
set ::env(RUN_CTS) 1
set ::env(DESIGN_IS_CORE) 0
set ::env(RT_MAX_LAYER) {met4}
set ::env(MAGIC_DEF_LABELS) 0
