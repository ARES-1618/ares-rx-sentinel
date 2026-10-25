"""
PRISM-RX Sentinel Cocotb Test Runner
Runs the full regression test suite with Icarus Verilog and Cocotb.
"""
import os
import sys
from cocotb_tools.runner import get_runner

def main():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    proj_dir = os.path.dirname(test_dir)
    src_dir = os.path.join(proj_dir, "src")

    sources = [
        "tt_um_prism_sentinel_project.v",
        "prism_sentinel_top.v",
        "prism_timing_sentinel.v",
        "prism_frame_fsm.v",
        "prism_fault_arbiter.v",
        "prism_fault_latch.v",
        "prism_isolation_gate.v",
        "prism_isolation_l3.v",
        "edge_detect.v",
        "state_machine.v",
        "data_multiplex.v",
        "serial_decode.v",
        "data_validate.v",
    ]
    verilog_sources = [os.path.join(src_dir, s) for s in sources]
    verilog_sources.append(os.path.join(test_dir, "tb.v"))

    runner = get_runner("icarus")
    runner.build(
        sources=verilog_sources,
        hdl_toplevel="tb",
        build_args=["-g2012", f"-I{src_dir}"],
        always=True,
    )

    runner.test(
        hdl_toplevel="tb",
        test_module="test",
        test_dir=test_dir,
        extra_env={"PYTHONPATH": test_dir},
        verbose=True,
    )

if __name__ == "__main__":
    main()
