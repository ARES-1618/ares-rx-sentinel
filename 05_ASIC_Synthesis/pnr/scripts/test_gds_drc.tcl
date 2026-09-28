gds read 05_ASIC_Synthesis/pnr/results/baseline/tt_um_dusterthefirst_project.gds
load tt_um_dusterthefirst_project
select top cell
expand
drc check
drc catchup
set cnt [drc list count total]
puts "TOTAL DRC ERRORS ON GDS: $cnt"
set why_list [drc listall why]
foreach {err count} $why_list {
    puts "$err : $count"
}
exit 0
