/*
 * ARES-RX Sentinel: Layer-1 Temporal Integrity Sentinel
 * Module: ares_timing_sentinel.v
 * Architecture: Reception Context Controller & Deferred Fault Classification
 * Target: Tiny Tapeout TT07/TT08 SkyWater 130nm ASIC
 * Standard: IEEE 1364-2005 Synthesizable Verilog
 */

`default_nettype none

module ares_timing_sentinel #(
    parameter integer HB_MIN      = 8,   // 400 us (Empirical half-bit min)
    parameter integer HB_MAX      = 10,  // 500 us (Empirical half-bit max)
    parameter integer BIT_MIN     = 16,  // 800 us (Empirical full-bit min)
    parameter integer BIT_MAX     = 20,  // 1000 us (Empirical full-bit max)
    parameter integer TIMEOUT_CYC = 21,  // 1050 us (Active gap threshold)
    parameter integer EOF_CYC     = 64   // 3200 us (End-of-burst confirmation)
)(
    input  wire       clk,
    input  wire       rst_n,
    input  wire       enable,

    input  wire       pos_edge,
    input  wire       neg_edge,

    output reg        reception_active, // 1 during active qualified transmission burst
    output reg        temporal_valid,   // Strobe 1 cycle when valid interval is verified
    output reg        temporal_fault,   // Strobe 1 cycle when temporal anomaly is detected
    output reg  [7:0] last_interval,    // Last measured interval duration for observability
    output reg  [2:0] fault_code,       // 001: Runt/Glitch, 010: Mid-band, 011: Gap Resume
    output reg  [1:0] current_state     // Diagnostic FSM state
);

    // Reception Context FSM State Encoding
    localparam [1:0] STATE_IDLE             = 2'b00;
    localparam [1:0] STATE_ARMED            = 2'b01;
    localparam [1:0] STATE_ACTIVE           = 2'b10;
    localparam [1:0] STATE_LONG_GAP_PENDING = 2'b11;

    // Fault Codes
    localparam [2:0] FAULT_NONE     = 3'b000;
    localparam [2:0] FAULT_RUNT     = 3'b001; // N <= 7 (Glitch)
    localparam [2:0] FAULT_MIDBAND  = 3'b010; // 11 <= N <= 15 (Mid-band violation)
    localparam [2:0] FAULT_GAP_RES  = 3'b011; // N >= 21 and edge resumed (Missing edge)

    reg [7:0] interval_counter;
    wire edge_detected = pos_edge | neg_edge;

    // Classification wires based on interval_counter at edge arrival
    wire is_runt     = (interval_counter < HB_MIN) && (interval_counter > 8'd0);
    wire is_half_bit = (interval_counter >= HB_MIN) && (interval_counter <= HB_MAX);
    wire is_midband  = (interval_counter > HB_MAX) && (interval_counter < BIT_MIN);
    wire is_full_bit = (interval_counter >= BIT_MIN) && (interval_counter <= BIT_MAX);
    wire is_valid    = is_half_bit | is_full_bit;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            interval_counter <= 8'd0;
            current_state    <= STATE_IDLE;
            reception_active <= 1'b0;
            temporal_valid   <= 1'b0;
            temporal_fault   <= 1'b0;
            fault_code       <= FAULT_NONE;
            last_interval    <= 8'd0;
        end else if (enable) begin
            // Default strobe clearing
            temporal_valid <= 1'b0;
            temporal_fault <= 1'b0;

            // Interval counter management:
            // On edge detection, capture interval duration and reset counter to 1
            // (since the edge cycle itself is cycle 1 of the new interval).
            if (edge_detected) begin
                last_interval    <= interval_counter;
                interval_counter <= 8'd1;
            end else if (interval_counter < 8'hFF) begin
                interval_counter <= interval_counter + 1'b1;
            end

            // Reception Context Controller & Fault Classifier
            case (current_state)
                STATE_IDLE: begin
                    reception_active <= 1'b0;
                    if (edge_detected) begin
                        // Candidate start of transmission observed
                        current_state <= STATE_ARMED;
                    end
                end

                STATE_ARMED: begin
                    reception_active <= 1'b0;
                    if (edge_detected) begin
                        if (is_valid) begin
                            // First valid interval establishes ACTIVE reception
                            temporal_valid   <= 1'b1;
                            reception_active <= 1'b1;
                            current_state    <= STATE_ACTIVE;
                        end else begin
                            // Unqualified settling transition before active reception:
                            // Re-arm using this new edge as reference candidate
                            current_state    <= STATE_ARMED;
                        end
                    end else if (interval_counter >= TIMEOUT_CYC) begin
                        // Isolated candidate edge was just noise / false alarm; return to IDLE
                        current_state <= STATE_IDLE;
                    end
                end

                STATE_ACTIVE: begin
                    reception_active <= 1'b1;
                    if (edge_detected) begin
                        if (is_valid) begin
                            temporal_valid <= 1'b1;
                            current_state  <= STATE_ACTIVE;
                        end else if (is_runt) begin
                            temporal_fault   <= 1'b1;
                            fault_code       <= FAULT_RUNT;
                            reception_active <= 1'b0;
                            current_state    <= STATE_IDLE;
                        end else if (is_midband) begin
                            temporal_fault   <= 1'b1;
                            fault_code       <= FAULT_MIDBAND;
                            reception_active <= 1'b0;
                            current_state    <= STATE_IDLE;
                        end
                    end else if (interval_counter >= TIMEOUT_CYC) begin
                        // Active gap exceeded 20 cycles -> Defer decision
                        current_state <= STATE_LONG_GAP_PENDING;
                    end
                end

                STATE_LONG_GAP_PENDING: begin
                    reception_active <= 1'b1;
                    if (edge_detected) begin
                        // Missing edge confirmed: transmission resumed after illegal gap >= 21
                        temporal_fault   <= 1'b1;
                        fault_code       <= FAULT_GAP_RES;
                        reception_active <= 1'b0;
                        current_state    <= STATE_IDLE;
                    end else if (interval_counter >= EOF_CYC) begin
                        // Normal end-of-burst confirmed: quiet interval persisted beyond EOF threshold
                        reception_active <= 1'b0;
                        current_state    <= STATE_IDLE;
                    end
                end

                default: begin
                    current_state    <= STATE_IDLE;
                    reception_active <= 1'b0;
                end
            endcase
        end
    end

endmodule

`default_nettype wire
