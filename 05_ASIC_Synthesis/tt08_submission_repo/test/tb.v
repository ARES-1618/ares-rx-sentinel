`default_nettype none
`timescale 1ns / 1ps

/*
 * ==============================================================================
 * Project: ARES-RX Sentinel — Tiny Tapeout TT08 Testbench
 * Module:  tb.v
 * Standard: Cocotb Test Wrapper
 * ==============================================================================
 */
module tb ();

  // Dump the signals to a VCD file.
  initial begin
    $dumpfile("tb.vcd");
    $dumpvars(0, tb);
    #1;
  end

  // Wire up the inputs and outputs:
  reg clk;
  reg rst_n;
  reg ena;

  // Named input pins
  reg rx_in;
  reg halt;
  reg [3:0] address;

  wire [7:0] ui_in = {address, 1'b0, halt, 1'b0, rx_in};
  wire [7:0] uio_in = 8'b00000000;
  wire [7:0] uo_out;
  wire [7:0] uio_out;
  wire [7:0] uio_oe;

  // Named output pins
  wire [7:0] parallel_out       = uo_out[7:0];
  wire       baseline_full      = uio_out[0];
  wire       manchester_clock   = uio_out[1];
  wire       manchester_data    = uio_out[2];
  wire       transmission_begin = uio_out[3];
  wire       base_neg_edge      = uio_out[4];
  wire       base_pos_edge      = uio_out[5];
  wire       tamper_alert       = uio_out[6];
  wire       reception_active   = uio_out[7];

  tt_um_ares_sentinel_project user_project (
`ifdef GL_TEST
      .VPWR(1'b1),
      .VGND(1'b0),
`endif
      .ui_in  (ui_in),    // Dedicated inputs
      .uo_out (uo_out),   // Dedicated outputs
      .uio_in (uio_in),   // IOs: Input path
      .uio_out(uio_out),  // IOs: Output path
      .uio_oe (uio_oe),   // IOs: Enable path
      .ena    (ena),      // enable - goes high when design is selected
      .clk    (clk),      // clock
      .rst_n  (rst_n)     // not reset
  );

endmodule
