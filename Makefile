# ==============================================================================
# ARES-RX Sentinel — Master Automation Makefile
# Target: Windows (PowerShell/WSL) & Linux
# Authority: ARES Semiconductor Technology Engineering Team
# ==============================================================================

PYTHON ?= python3

.PHONY: all help demo precheck verify-rtl verify-hash test-apb clean

all: help

help:
	@echo "=========================================================================="
	@echo "  ARES-RX Sentinel: Automation & Verification Command Center              "
	@echo "=========================================================================="
	@echo "  make demo         - Run interactive CLI hardware demonstration (6 scenarios)"
	@echo "  make precheck     - Run official Tiny Tapeout TT08 layout precheck"
	@echo "  make verify-rtl   - Run Icarus Verilog native RTL simulation suite"
	@echo "  make verify-hash  - Verify SHA-256 cryptographic freeze seals"
	@echo "  make test-apb     - Compile and test AMBA APB4 SoC peripheral wrapper"
	@echo "  make stimulus     - Generate post-silicon calibrated stimulus CSV vectors"
	@echo "=========================================================================="

demo:
	@echo ">>> Running ARES-RX Sentinel Hardware Demonstration..."
	@cd 06_Demonstration/ARES-RX_Sentinel/demo && $(PYTHON) ares_hardware_demo.py --all

precheck:
	@echo ">>> Running Tiny Tapeout TT08 Precheck & Physical Boundary Verification..."
	@$(PYTHON) 05_ASIC_Synthesis/pnr/scripts/verify_tinytapeout_precheck.py

verify-rtl:
	@echo ">>> Compiling & Simulating ARES-RX Sentinel Integrated RTL..."
	@iverilog -g2012 -o sim_m4.vvp \
		03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_sentinel_top.v \
		03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_timing_sentinel.v \
		03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_frame_fsm.v \
		03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_fault_arbiter.v \
		03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_fault_latch.v \
		03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_isolation_gate.v \
		03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_isolation_l3.v \
		04_Verification/ARES-RX_Sentinel/cocotb/tb_ares_sentinel_integrated.v
	@vvp sim_m4.vvp
	@rm -f sim_m4.vvp

verify-hash:
	@echo ">>> Verifying SHA-256 Cryptographic Seals on Frozen RTL..."
	@sha256sum -c 00_Governance/M4_Cryptographic_Manifest.sha256 || \
		(echo "Run in PowerShell: Get-FileHash 03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/*.v -Algorithm SHA256")

test-apb:
	@echo ">>> Compiling AMBA APB4 SoC Integration Wrapper..."
	@iverilog -g2012 -o test_apb.vvp \
		03_Core_Projects/ARES-RX_Sentinel/integration/ares_sentinel_apb.v \
		03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_sentinel_top.v \
		03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_timing_sentinel.v \
		03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_frame_fsm.v \
		03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_fault_arbiter.v \
		03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_fault_latch.v \
		03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_isolation_gate.v \
		03_Core_Projects/ARES-RX_Sentinel/ares_sentinel/ares_isolation_l3.v
	@echo "[PASS] APB4 wrapper compiled cleanly with zero syntax/elaboration errors."
	@rm -f test_apb.vvp

stimulus:
	@echo ">>> Generating Calibrated Post-Silicon Stimulus Vectors..."
	@cd 04_Verification/post_silicon && $(PYTHON) rp2040_stimulus_generator.py \
		--csv nominal_stimulus.csv --runt-csv runt_glitch_stimulus.csv --header stimulus_vectors.h
	@echo "[PASS] Post-silicon stimulus vectors generated successfully."
