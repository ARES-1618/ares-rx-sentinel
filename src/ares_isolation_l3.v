/*
 * ARES-RX Sentinel: Layer-3 Hardware Fail-Closed Isolation
 * Module: ares_isolation_l3.v
 * Architecture: Integrated Layer-3 Enclosure (Fault Latch + Isolation Gate)
 * Target: Tiny Tapeout TT07/TT08 SkyWater 130nm ASIC
 * Standard: IEEE 1364-2005 Synthesizable Verilog
 */

`default_nettype none

module ares_isolation_l3 #(
    parameter integer DATA_WIDTH = 8
)(
    input  wire                  clk,
    input  wire                  rst_n,

    // Fault Detection Trigger Inputs (from M1/M3)
    input  wire                  temporal_fault,     // Strobe from Layer-1 Timing Sentinel
    input  wire [2:0]            fault_code,         // Fault code from Layer-1 Timing Sentinel

    // Data Path Inputs (from Decoder / Downstream)
    input  wire [DATA_WIDTH-1:0] raw_data_in,        // Decoded payload data
    input  wire                  raw_valid_in,       // Decoded data valid flag

    // Security & Data Outputs
    output wire [DATA_WIDTH-1:0] safe_data_out,      // Zeroized when fault_latched
    output wire                  safe_valid_out,     // Suppressed when fault_latched
    output wire                  fault_latched,      // Steady active-high fault state
    output wire                  tamper_alert,       // Hardware security alert output pin

    // Observability / Diagnostic Outputs
    output wire [2:0]            latched_fault_code  // First-cause latched fault code
);

    // Instantiate Sticky Fault Latch
    ares_fault_latch u_fault_latch (
        .clk(clk),
        .rst_n(rst_n),
        .set_fault(temporal_fault),
        .fault_code_in(fault_code),
        .fault_latched(fault_latched),
        .latched_fault_code(latched_fault_code)
    );

    // Instantiate Combinational Isolation Gate
    ares_isolation_gate #(
        .DATA_WIDTH(DATA_WIDTH)
    ) u_isolation_gate (
        .fault_latched(fault_latched),
        .in_data(raw_data_in),
        .in_valid(raw_valid_in),
        .out_data(safe_data_out),
        .out_valid(safe_valid_out),
        .tamper_alert(tamper_alert)
    );

endmodule

`default_nettype wire
