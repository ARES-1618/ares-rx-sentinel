/*
 * ==============================================================================
 * Project: ARES-RX Sentinel — Trusted Physical/Digital Demarcation Boundary
 * Module:  tt_um_ares_sentinel_project
 * Standard: Tiny Tapeout TT08 (SkyWater 130nm ASIC — sky130_fd_sc_hd)
 * Authority: Technical Architect / Research Direction
 *
 * Description:
 *   Top-level ASIC perimeter wrapper integrating the protected Sentinel
 *   subsystem (ares_sentinel_top.v) with the baseline Manchester receiver
 *   core (tt07-bep-decode). Provides physical pin mapping to Tiny Tapeout
 *   tile IOs, fail-closed safe data outputs, and dedicated telemetry pins.
 * ==============================================================================
 */

`default_nettype none

module tt_um_ares_sentinel_project (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs (Gated Safe Parallel Out)
    input  wire [7:0] uio_in,   // IOs: Bidirectional input path
    output wire [7:0] uio_out,  // IOs: Bidirectional output path
    output wire [7:0] uio_oe,   // IOs: Output enable (1 = output, 0 = input)
    input  wire       ena,      // Tiny Tapeout enable strobe (always 1 when active)
    input  wire       clk,      // System Master Clock (20 kHz nominal)
    input  wire       rst_n     // Active-Low Hardware Asynchronous Reset
);

    // --------------------------------------------------------------------------
    // Physical Digital Pin Mapping & Epistemic Boundary Clarification
    // --------------------------------------------------------------------------
    // ARCHITECTURAL BOUNDARY:
    //   433 MHz RF Carrier -> External RF Front-End (Antenna + LNA + Mixer)
    //                      -> Demodulator / Comparator IC
    //                      -> Demodulated Digital Baseband Signal (rx_digital)
    //                      -> Tiny Tapeout Dedicated Digital Input ui_in[0]
    //                      -> ARES-RX Sentinel Perimeter & Demodulator Core
    //
    // ui_in[0] is strictly a digital CMOS GPIO input, NOT an RF antenna port.
    wire rx_digital = ui_in[0];         // Demodulated baseband digital RX input
    wire halt       = ui_in[2];         // Output enable / halt control from baseline
    wire [3:0] address = ui_in[7:4];    // 4-bit multiplexer read address

    // Unused input termination to prevent floating gates / synthesis warnings
    wire _unused = &{1'b0, ena, ui_in[1], ui_in[3], uio_in};

    // --------------------------------------------------------------------------
    // Baseline Core Wires
    // --------------------------------------------------------------------------
    wire base_pos_edge;
    wire base_neg_edge;
    wire manchester_clock;
    wire manchester_data;
    wire transmission_begin;
    wire base_full;
    wire [7:0] raw_parallel_out;

    // --------------------------------------------------------------------------
    // Sentinel Protected Wires
    // --------------------------------------------------------------------------
    wire [7:0] safe_data_out;
    wire       safe_valid_out;
    wire       tamper_alert;
    wire [2:0] latched_fault_code;
    wire       reception_active;
    wire       frame_complete;
    wire       temporal_fault;
    wire [2:0] temporal_code;
    wire       frame_fault;
    wire [2:0] frame_code;
    wire       arb_set_fault;
    wire [2:0] arb_fault_code;
    wire [7:0] bit_counter;
    wire       fault_latched;

    // --------------------------------------------------------------------------
    // Baseline Demodulator Core Instantiation (Frozen Reference)
    // --------------------------------------------------------------------------
    edge_detect u_base_edge (
        .digital_in(rx_digital),
        .clock(clk),
        .reset_n(rst_n),
        .pos_edge(base_pos_edge),
        .neg_edge(base_neg_edge)
    );

    state_machine u_base_fsm (
        .clock(clk),
        .enable(!halt),
        .reset_n(rst_n),
        .pos_edge(base_pos_edge),
        .neg_edge(base_neg_edge),
        .manchester_clock(manchester_clock),
        .manchester_data(manchester_data),
        .transmission_begin(transmission_begin)
    );

    data_multiplex u_base_mux (
        .reset_n(!transmission_begin && rst_n),
        .clock(clk),
        .serial_clock(manchester_clock),
        .serial_data(manchester_data),
        .address(address),
        .parallel_out(raw_parallel_out),
        .full(base_full)
    );

    // --------------------------------------------------------------------------
    // Integrated Sentinel Demarcation Subsystem (Layer 1 + 2 + Arbiter + 3)
    // --------------------------------------------------------------------------
    ares_sentinel_top #(
        .DATA_WIDTH(8)
    ) u_sentinel_top (
        .clk(clk),
        .rst_n(rst_n),
        .rx_in(rx_digital),
        .ext_pos_edge(1'b0),
        .ext_neg_edge(1'b0),
        .use_ext_edges(1'b0),
        .serial_clock(manchester_clock),
        .serial_data(manchester_data),
        .raw_data_in(raw_parallel_out),
        .raw_valid_in(base_full),
        .safe_data_out(safe_data_out),
        .safe_valid_out(safe_valid_out),
        .tamper_alert(tamper_alert),
        .latched_fault_code(latched_fault_code),
        .reception_active(reception_active),
        .frame_complete(frame_complete),
        .temporal_fault(temporal_fault),
        .temporal_code(temporal_code),
        .frame_fault(frame_fault),
        .frame_code(frame_code),
        .arb_set_fault(arb_set_fault),
        .arb_fault_code(arb_fault_code),
        .bit_counter(bit_counter),
        .fault_latched(fault_latched)
    );

    // --------------------------------------------------------------------------
    // Fail-Closed Dedicated Output Assignment
    // --------------------------------------------------------------------------
    // Dedicated output bus is driven by fail-closed zeroized safe_data_out,
    // additionally qualified with baseline halt control.
    assign uo_out = safe_data_out & {8{halt}};

    // --------------------------------------------------------------------------
    // Bidirectional Telemetry Pinout Assignment & Direction Control
    // --------------------------------------------------------------------------
    // Pins 0..5 maintain backward-compatibility with baseline pinout contract.
    // Pins 6 and 7 (unused 2'b00 in baseline) are allocated to Sentinel telemetry:
    //   uio_out[6] : tamper_alert (Persistent security alarm)
    //   uio_out[7] : reception_active (Physical RF envelope monitor)
    assign uio_out[0] = base_full;
    assign uio_out[1] = manchester_clock;
    assign uio_out[2] = manchester_data;
    assign uio_out[3] = transmission_begin;
    assign uio_out[4] = base_neg_edge;
    assign uio_out[5] = base_pos_edge;
    assign uio_out[6] = tamper_alert;
    assign uio_out[7] = reception_active;

    // Dedicated Output Enable (OE) configuration:
    // All 8 bidirectional pins are actively driven outputs (1 = output).
    // uio_in is cleanly terminated into _unused to prevent floating input gates.
    assign uio_oe[5:0] = 6'b111111; // Baseline telemetry channels
    assign uio_oe[6]   = 1'b1;      // Sentinel tamper_alert output enable
    assign uio_oe[7]   = 1'b1;      // Sentinel reception_active output enable

endmodule

`default_nettype wire
