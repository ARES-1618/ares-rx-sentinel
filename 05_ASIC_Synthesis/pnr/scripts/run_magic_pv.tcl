# ==============================================================================
# Magic Physical Verification Script: GDS Merge, DRC, & SPICE Extraction
# PDK: SkyWater 130nm (sky130_fd_sc_hd)
# Standard: Tiny Tapeout TT08
# ==============================================================================

if { ! [info exists ::env(TOP_MODULE)] || ! [info exists ::env(DEF_FILE)] || ! [info exists ::env(OUT_DIR)] } {
    puts stderr "Error: Required environment variables TOP_MODULE, DEF_FILE, OUT_DIR must be set."
    exit 1
}

set top_module $::env(TOP_MODULE)
set def_file $::env(DEF_FILE)
set out_dir $::env(OUT_DIR)
set gds_lib "05_ASIC_Synthesis/pdk/sky130_fd_sc_hd.gds"

puts "=== Step 1/4: Reading Standard Cell GDS Library ==="
gds readonly true
gds rescale false
gds read $gds_lib

puts "=== Step 2/4: Reading Routed DEF File ==="
def read $def_file

puts "=== Step 3/4: Loading Top Cell & Writing Merged GDS ==="
load $top_module
select top cell
expand
gds write "${out_dir}/${top_module}.gds"
puts "Merged GDS written to: ${out_dir}/${top_module}.gds"

puts "=== Step 4/4: DRC Check & SPICE Extraction for LVS ==="
drc check
drc catchup
set drc_errors [drc list count total]
puts "TOTAL DRC ERRORS: $drc_errors"

set drc_file [open "${out_dir}/${top_module}_drc.log" w]
puts $drc_file "DRC Report for $top_module"
puts $drc_file "Total DRC Errors: $drc_errors"
if { $drc_errors > 0 } {
    set why_list [drc listall why]
    foreach {err count} $why_list {
        puts $drc_file "$err : $count"
    }
}
close $drc_file

# SPICE Extraction for LVS
extract do local
extract no capacitance
extract no coupling
extract no resistance
extract all
ext2spice lvs
ext2spice -o "${out_dir}/${top_module}_extracted.spice"
puts "Extracted SPICE written to: ${out_dir}/${top_module}_extracted.spice"

exit 0
