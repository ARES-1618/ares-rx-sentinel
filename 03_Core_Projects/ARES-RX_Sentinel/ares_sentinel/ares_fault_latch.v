/*
 * ARES-RX Sentinel: Layer-3 Hardware Fail-Closed Isolation
 * Module: ares_fault_latch.v
 * Architecture: Sticky Fault Latch & First-Cause Diagnostic Register
 * Target: Tiny Tapeout TT07/TT08 SkyWater 130nm ASIC
 * Standard: IEEE 1364-2005 Synthesizable Verilog
 */

`default_nettype none

module ares_fault_latch (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       set_fault,          // Single-cycle fault trigger (from M1/M3)
    input  wire [2:0] fault_code_in,      // Fault category from detector
    output reg        fault_latched,      // Sticky fault state (1 = locked)
    output reg  [2:0] latched_fault_code  // First-cause latched fault code
);

    localparam [2:0] FAULT_NONE = 3'b000;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            fault_latched      <= 1'b0;
            latched_fault_code <= FAULT_NONE;
        end else begin
            if (set_fault) begin
                fault_latched <= 1'b1;
                // Capture first-cause fault code; do not overwrite if already latched
                if (!fault_latched) begin
                    latched_fault_code <= fault_code_in;
                end
            end
        end
    end

endmodule

`default_nettype wire
