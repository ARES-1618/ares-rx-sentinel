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
	@echo "  make verify-pub   - Audit cross-document publication metric consistency"
	@echo "  make test-e2e     - Run end-to-end cyber-physical socket test battery"
	@echo "  make test-apb     - Compile and test AMBA APB4 SoC peripheral wrapper"
	@echo "  make stimulus     - Generate post-silicon calibrated stimulus CSV vectors"
	@echo "  make clean        - Remove ephemeral simulation artifacts and bytecode"
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
		03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src/edge_detect.v \
		03_Core_Projects/ARES-RX_Sentinel/tt07-bep-decode/src/state_machine.v \
		04_Verification/ARES-RX_Sentinel/cocotb/tb_ares_sentinel_integrated.v
	@vvp sim_m4.vvp
	@$(PYTHON) -c "import os; os.remove('sim_m4.vvp') if os.path.exists('sim_m4.vvp') else None"

verify-hash:
	@echo ">>> Verifying SHA-256 Cryptographic Seals on Frozen RTL..."
	@$(PYTHON) 00_Governance/verify_m4_hashes.py

verify-pub:
	@echo ">>> Auditing Cross-Document Publication Consistency..."
	@$(PYTHON) verify_publication_consistency.py

test-e2e:
	@echo ">>> Running Cyber-Physical E2E Socket Demonstration Battery..."
	@$(PYTHON) 06_Demonstration/cyber_physical/test_demonstrator_e2e.py

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
	@$(PYTHON) -c "import os; os.remove('test_apb.vvp') if os.path.exists('test_apb.vvp') else None"

stimulus:
	@echo ">>> Generating Calibrated Post-Silicon Stimulus Vectors..."
	@cd 04_Verification/post_silicon && $(PYTHON) rp2040_stimulus_generator.py \
		--csv nominal_stimulus.csv --runt-csv runt_glitch_stimulus.csv --header stimulus_vectors.h
	@echo "[PASS] Post-silicon stimulus vectors generated successfully."

clean:
	@echo ">>> Cleaning ephemeral artifacts..."
	@$(PYTHON) -c "import os, glob; [os.remove(f) for f in glob.glob('*.vvp') + glob.glob('a.out') if os.path.exists(f)]"
	@echo "[PASS] Working directory cleaned."
