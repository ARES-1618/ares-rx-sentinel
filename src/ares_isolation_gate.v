/*
 * ARES-RX Sentinel: Layer-3 Hardware Fail-Closed Isolation
 * Module: ares_isolation_gate.v
 * Architecture: Pure Combinational Zeroization & Tamper Alert Gate
 * Target: Tiny Tapeout TT07/TT08 SkyWater 130nm ASIC
 * Standard: IEEE 1364-2005 Synthesizable Verilog
 */

`default_nettype none

module ares_isolation_gate #(
    parameter integer DATA_WIDTH = 8
)(
    input  wire                  fault_latched,  // Sticky fault state from latch
    input  wire [DATA_WIDTH-1:0] in_data,        // Payload data bus from decoder
    input  wire                  in_valid,       // Valid / full strobe from decoder
    output wire [DATA_WIDTH-1:0] out_data,       // Fail-closed isolated output data
    output wire                  out_valid,      // Gated valid strobe
    output wire                  tamper_alert    // Hardware security alert output pin
);

    // Pure combinational zeroization:
    // Adds ZERO additional clock-cycle latency once fault_latched asserts.
    assign out_data     = fault_latched ? {DATA_WIDTH{1'b0}} : in_data;
    assign out_valid    = fault_latched ? 1'b0               : in_valid;
    assign tamper_alert = fault_latched;

endmodule

`default_nettype wire
