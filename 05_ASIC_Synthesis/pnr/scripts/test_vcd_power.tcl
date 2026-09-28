read_liberty 05_ASIC_Synthesis/pdk/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog 05_ASIC_Synthesis/pnr/results/top/top_routed.v
link_design tt_um_ares_sentinel_project
read_spef 05_ASIC_Synthesis/pnr/results/top/top_routed.spef
create_clock -period 50000 clk

puts "=== Testing read_power_activities ==="
if {[catch {read_power_activities -vcd 04_Verification/ARES-RX_Sentinel/waveforms/ares_sentinel_integrated.vcd -scope tb_ares_sentinel_integrated/u_sentinel_top} err]} {
    puts "read_power_activities error: $err"
} else {
    puts "read_power_activities SUCCESS!"
    report_power
}
exit 0
