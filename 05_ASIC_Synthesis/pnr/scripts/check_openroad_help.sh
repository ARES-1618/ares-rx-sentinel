#!/bin/bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
openroad -exit -no_init -no_splash << 'EOF'
help write_verilog
EOF
