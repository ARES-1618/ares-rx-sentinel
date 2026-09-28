/*
 * ARES-RX Sentinel: Layer-2/Layer-3 Upstream Fault Priority Arbiter
 * Module: ares_fault_arbiter.v
 * Architecture: Pure Combinational Priority Resolver (L1 Physical > L2 Protocol)
 * Target: Tiny Tapeout TT07/TT08 SkyWater 130nm ASIC
 * Standard: IEEE 1364-2005 Synthesizable Verilog
 *
 * Operational Principles:
 * 1. Stateless & Pure Combinational: Zero clock cycle latency delay.
 * 2. Same-Cycle Arbitration Priority:
 *    - Priority 1: Layer-1 Temporal Fault (Physical signal / timing violation)
 *    - Priority 2: Layer-2 Frame Syntax Fault (Protocol structure violation)
 * 3. Cross-Cycle Persistence: Handled downstream by ares_fault_latch.v (M2).
 *    Arbitration is strictly same-cycle; latch preserves first-cause across time.
 */

`default_nettype none

module ares_fault_arbiter (
    // Layer-1 Fault Inputs (Temporal Sentinel - Highest Priority)
    input  wire       temporal_fault,
    input  wire [2:0] temporal_code,

    // Layer-2 Fault Inputs (Frame Syntax FSM - Secondary Priority)
    input  wire       frame_fault,
    input  wire [2:0] frame_code,

    // Resolved Fault Outputs (To Layer-3 Sticky Fault Latch)
    output reg        set_fault,
    output reg  [2:0] fault_code
);

    localparam [2:0] FAULT_NONE = 3'b000;

    always @(*) begin
        if (temporal_fault) begin
            set_fault  = 1'b1;
            fault_code = temporal_code;
        end else if (frame_fault) begin
            set_fault  = 1'b1;
            fault_code = frame_code;
        end else begin
            set_fault  = 1'b0;
            fault_code = FAULT_NONE;
        end
    end

endmodule

`default_nettype wire
