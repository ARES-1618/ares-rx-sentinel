# ==============================================================================
# Synopsys Design Constraints (SDC) — ARES-RX Sentinel ASIC
# Standard: Tiny Tapeout TT08 (SkyWater 130nm — sky130_fd_sc_hd)
# Authority: Technical Architect / Research Direction (WO-2026-M5-001-ARCH-REV-A)
#
# ARCHITECTURAL EPISTEMIC BOUNDARY & CLOCK SEMANTICS:
# 1. Operational Protocol Clock:
#    - Nominal Frequency: F_clk = 20 kHz (Period = 50,000.0 ns).
#    - All temporal integrity windows (N_HB = 8..10, N_BIT = 16..20, N_EOF = 64)
#      derive physical meaning strictly from T_clk = 50.0 us.
#
# 2. Static Timing Analysis (STA) Stress Target:
#    - Stress Frequency: 50 MHz (Period = 20.0 ns).
#    - Purpose: Exclusively used during STA / P&R to determine silicon critical
#      path delay (T_crit), establish setup/hold margin, and calculate the
#      theoretical maximum circuit cutoff frequency (F_max = 1 / T_crit).
#    - Warning: 50 MHz is NEVER an equivalent functional operating mode.
# ==============================================================================

# Clock Definition
if { [info exists ::env(STRESS_50MHZ)] && $::env(STRESS_50MHZ) == 1 } {
    # 50 MHz STA stress target (T = 20.0 ns)
    create_clock -name clk -period 20.000 [get_ports clk]
} else {
    # 20 kHz nominal operational clock (T = 50,000.0 ns)
    create_clock -name clk -period 50000.000 [get_ports clk]
}

# Clock Uncertainty & Slew Margin
set_clock_uncertainty 0.100 [get_clocks clk]
set_clock_transition 0.150 [get_clocks clk]

# External IO Delays (budgeted at 25% of period under 50 MHz stress, or 5 ns nominal)
set_input_delay -clock clk -max 5.000 [get_ports {ui_in[*] uio_in[*] rst_n ena}]
set_input_delay -clock clk -min 1.000 [get_ports {ui_in[*] uio_in[*] rst_n ena}]

set_output_delay -clock clk -max 5.000 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]
set_output_delay -clock clk -min 1.000 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]

# Standard Tiny Tapeout pad capacitive load: 30 fF
set_load 0.030 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]
