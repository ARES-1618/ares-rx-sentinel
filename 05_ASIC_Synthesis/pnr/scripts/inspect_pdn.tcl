puts "=== ALL PDN COMMANDS ==="
foreach c [info commands *pdn*] {
    puts "  GLOBAL: $c"
}
foreach c [info commands ::pdn::*] {
    puts "  PDN: $c"
}
foreach c [info commands ::pdngen::*] {
    puts "  PDNGEN: $c"
}
exit 0
