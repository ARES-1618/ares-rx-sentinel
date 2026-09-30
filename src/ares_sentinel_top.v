/*
 * ARES-RX Sentinel: Top-Level Trusted Physical/Digital Demarcation Boundary
 * Module: ares_sentinel_top.v
 * Architecture: Integrated L1 Timing Sentinel + L2 Frame Syntax FSM + Arbiter + L3 Fail-Closed Isolation
 * Target: Tiny Tapeout TT07/TT08 SkyWater 130nm ASIC
 * Standard: IEEE 1364-2005 Synthesizable Verilog
 *
 * Operational Hierarchy:
 *  rx_in -------------> [Layer-1: ares_timing_sentinel] ---> temporal_fault, temporal_code, reception_active
 *                                                                   |
 *  serial_clock/data -> [Layer-2: ares_frame_fsm] ---------> frame_fault, frame_code, frame_complete
 *                                                                   |
 *                       [Arbiter: ares_fault_arbiter] ------> set_fault, fault_code (L1 > L2)
 *                                                                   |
 *  raw_data_in/valid -> [Layer-3: ares_isolation_l3] ------> safe_data_out, safe_valid_out, tamper_alert
 */

`default_nettype none

module ares_sentinel_top #(
    parameter integer DATA_WIDTH = 8
)(
    input  wire                  clk,
    input  wire                  rst_n,

    // Physical Digital Demarcation Input
    input  wire                  rx_in,

    // Optional direct edge inputs (if use_ext_edges=0, internal edge detector is used)
    input  wire                  ext_pos_edge,
    input  wire                  ext_neg_edge,
    input  wire                  use_ext_edges,

    // Demodulated / Decoded Stream Inputs (from Manchester Demodulator)
    input  wire                  serial_clock,
    input  wire                  serial_data,

    // Downstream Parallel Data Path Inputs (from Deserializer / Host)
    input  wire [DATA_WIDTH-1:0] raw_data_in,
    input  wire                  raw_valid_in,

    // Gated & Isolated Safe Outputs
    output wire [DATA_WIDTH-1:0] safe_data_out,
    output wire                  safe_valid_out,
    output wire                  tamper_alert,
    output wire [2:0]            latched_fault_code,

    // Diagnostic & Observability Outputs
    output wire                  reception_active,
    output wire                  frame_complete,
    output wire                  temporal_fault,
    output wire [2:0]            temporal_code,
    output wire                  frame_fault,
    output wire [2:0]            frame_code,
    output wire                  arb_set_fault,
    output wire [2:0]            arb_fault_code,
    output wire [7:0]            bit_counter,
    output wire                  fault_latched
);

    // Internal Edge Detection on rx_in
    reg previous_in;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            previous_in <= 1'b0;
        end else begin
            previous_in <= rx_in;
        end
    end

    wire int_pos_edge = !previous_in & rx_in;
    wire int_neg_edge = previous_in & !rx_in;

    wire active_pos_edge = use_ext_edges ? ext_pos_edge : int_pos_edge;
    wire active_neg_edge = use_ext_edges ? ext_neg_edge : int_neg_edge;

    // Diagnostic internal wires
    wire [7:0] edge_interval_diag;
    wire       temporal_valid_diag;
    wire [1:0] l1_state_diag;
    wire [1:0] l2_state_diag;

    // -------------------------------------------------------------
    // Layer 1: Temporal Integrity Sentinel (Physical Timing & Context)
    // -------------------------------------------------------------
    ares_timing_sentinel u_timing_sentinel (
        .clk(clk),
        .rst_n(rst_n),
        .enable(1'b1),
        .pos_edge(active_pos_edge),
        .neg_edge(active_neg_edge),
        .reception_active(reception_active),
        .temporal_valid(temporal_valid_diag),
        .temporal_fault(temporal_fault),
        .last_interval(edge_interval_diag),
        .fault_code(temporal_code),
        .current_state(l1_state_diag)
    );

    // -------------------------------------------------------------
    // Layer 2: Frame Syntax Integrity Monitor (Protocol Structure)
    // -------------------------------------------------------------
    ares_frame_fsm u_frame_fsm (
        .clk(clk),
        .rst_n(rst_n),
        .serial_clock(serial_clock),
        .serial_data(serial_data),
        .reception_active(reception_active),
        .frame_fault(frame_fault),
        .frame_fault_code(frame_code),
        .frame_complete(frame_complete),
        .bit_counter(bit_counter),
        .current_state(l2_state_diag)
    );

    // -------------------------------------------------------------
    // Upstream Fault Priority Arbiter (Pure Combinational: L1 > L2)
    // -------------------------------------------------------------
    ares_fault_arbiter u_fault_arbiter (
        .temporal_fault(temporal_fault),
        .temporal_code(temporal_code),
        .frame_fault(frame_fault),
        .frame_code(frame_code),
        .set_fault(arb_set_fault),
        .fault_code(arb_fault_code)
    );

    // -------------------------------------------------------------
    // Layer 3: Hardware Fail-Closed Security Policy Enforcement
    // -------------------------------------------------------------
    ares_isolation_l3 #(
        .DATA_WIDTH(DATA_WIDTH)
    ) u_isolation_l3 (
        .clk(clk),
        .rst_n(rst_n),
        .temporal_fault(arb_set_fault),
        .fault_code(arb_fault_code),
        .raw_data_in(raw_data_in),
        .raw_valid_in(raw_valid_in),
        .safe_data_out(safe_data_out),
        .safe_valid_out(safe_valid_out),
        .fault_latched(fault_latched),
        .tamper_alert(tamper_alert),
        .latched_fault_code(latched_fault_code)
    );

endmodule

`default_nettype wire
