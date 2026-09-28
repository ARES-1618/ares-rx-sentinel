puts "=== NAMESPACES ==="
puts [namespace children ::]
puts "=== PDN COMMANDS ==="
puts [info commands pdn::*]
puts "=== GLOBAL COMMANDS ==="
puts [info commands *global*]
puts "=== ORD COMMANDS ==="
puts [info commands ord::*]
exit 0
