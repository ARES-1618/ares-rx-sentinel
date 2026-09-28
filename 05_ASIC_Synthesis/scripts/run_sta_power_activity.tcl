# ==============================================================================
# OpenSTA Activity-Dependent Power Characterization Script
# Target Process: SkyWater 130nm Standard Cells (sky130_fd_sc_hd)
# Corner: TT / 25C / 1.80V (sky130_fd_sc_hd__tt_025C_1v80.lib)
# Work Order: WO-2026-M5-E-CLOSE-001
# ==============================================================================

set report_file "05_ASIC_Synthesis/results/sta_power_activity_sweep.txt"
set fp [open $report_file "w"]
puts $fp "================================================================================"
puts $fp "ARES-RX SENTINEL — ACTIVITY-DEPENDENT POWER CHARACTERIZATION MATRIX"
puts $fp "Corner: SkyWater 130nm sky130_fd_sc_hd__tt_025C_1v80 (TT, 25C, 1.80V)"
puts $fp "Tool: OpenSTA 2.0.17 | Work Order: WO-2026-M5-E-CLOSE-001"
puts $fp "================================================================================\n"
close $fp

# Procedure to characterize power across frequencies and activities
proc characterize_design {design_name verilog_path top_module is_tt_shell} {
    global report_file
    set lib_path "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib"
    
    set fp [open $report_file "a"]
    puts $fp "################################################################################"
    puts $fp "DESIGN: $design_name ($top_module)"
    puts $fp "Netlist: $verilog_path"
    puts $fp "################################################################################\n"
    close $fp

    set freqs { { "20 kHz (Operational Protocol)" 50000.000 } { "50 MHz (STA Stress Target)" 20.000 } }
    set activities { { "Default (Tool Default)" "" "" } { "Low (alpha = 0.05, duty = 0.5)" 0.05 0.5 } { "Nominal (alpha = 0.10, duty = 0.5)" 0.10 0.5 } { "Elevated (alpha = 0.20, duty = 0.5)" 0.20 0.5 } }

    foreach freq_info $freqs {
        set freq_label [lindex $freq_info 0]
        set period_ns [lindex $freq_info 1]

        set fp [open $report_file "a"]
        puts $fp "--------------------------------------------------------------------------------"
        puts $fp ">>> FREQUENCY: $freq_label (T = $period_ns ns)"
        puts $fp "--------------------------------------------------------------------------------"
        close $fp

        foreach act_info $activities {
            set act_label [lindex $act_info 0]
            set alpha [lindex $act_info 1]
            set duty [lindex $act_info 2]

            # Re-read liberty and netlist for pristine state
            read_liberty $lib_path
            read_verilog $verilog_path
            link_design $top_module

            create_clock -name clk -period $period_ns [get_ports clk]

            if {$is_tt_shell} {
                set_input_delay -clock clk 5.000 [get_ports {ui_in[*] uio_in[*] rst_n ena}]
                set_output_delay -clock clk 5.000 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]
                set_load 0.030 [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]
            } else {
                set_input_delay -clock clk 5.000 [all_inputs]
                set_output_delay -clock clk 5.000 [all_outputs]
                set_load 0.030 [all_outputs]
            }

            if {$alpha != ""} {
                set_power_activity -input -activity $alpha -duty $duty
            }

            set fp [open $report_file "a"]
            puts $fp "--- Condition: Activity = $act_label ---"
            close $fp

            report_power >> $report_file

            set fp [open $report_file "a"]
            puts $fp ""
            close $fp
        }
    }
}

# 1. Baseline Unprotected (B)
characterize_design "Baseline Unprotected (B)" "05_ASIC_Synthesis/results/baseline_synth_netlist.v" "tt_um_dusterthefirst_project" 1

# 2. Sentinel Core Subsystem (S_core)
characterize_design "Sentinel Core Subsystem (S_core)" "05_ASIC_Synthesis/results/sentinel_synth_netlist.v" "ares_sentinel_top" 0

# 3. Integrated Protected Top (S_top)
characterize_design "Integrated Protected Top (S_top)" "05_ASIC_Synthesis/results/top_synth_netlist.v" "tt_um_ares_sentinel_project" 1

exit
