#!/bin/bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
openroad -exit -no_init -no_splash << 'EOF'
help read_vcd
help read_saif
help set_power_activity
EOF
