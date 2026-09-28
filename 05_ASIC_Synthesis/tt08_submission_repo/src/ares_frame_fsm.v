/*
 * ARES-RX Sentinel: Layer-2 Frame Syntax Integrity Monitor
 * Module: ares_frame_fsm.v
 * Architecture: Autonomous 192-Bit Frame Integrity FSM & Bit-Position Verifier
 * Target: Tiny Tapeout TT07/TT08 SkyWater 130nm ASIC
 * Standard: IEEE 1364-2005 Synthesizable Verilog
 *
 * Operational Principles & Invariants:
 * 1. Autonomous Bit Counter:
 *    - Owns its own 8-bit frame counter (0..191) on posedge clk && (serial_clock == 1'b1).
 *    - Zero dependency on baseline `full` signal for security enforcement.
 * 2. Immediate Sample-Time Field Verification:
 *    - Bits 0..31  : Preamble (32'hAAAAAAAA). Bit mismatch -> FAULT_PREAMBLE_CORRUPT (3'b100).
 *    - Bits 32..47 : Type 1 (16'hD391). Bit mismatch -> FAULT_TYPE_CORRUPT (3'b101).
 *    - Bits 48..63 : Type 2 (16'hD391). Bit mismatch -> FAULT_TYPE_CORRUPT (3'b101).
 *    - Bits 64..95 : Constant (32'h0DFFFFFE). Bit mismatch -> FAULT_CONSTANT_CORRUPT (3'b110).
 * 3. Dynamic Payload Transparency:
 *    - Bits 96..167: Dynamic payload (72b: ID, Room, Set, State).
 *    - Consumed purely by bit counter. Values are NOT checked, ensuring nominal compatibility.
 * 4. Protocol Trailer:
 *    - Bits 168..191: Reserved protocol trailer (24b). Consumed without CRC assumptions.
 * 5. Qualified Truncation & Overrun:
 *    - Truncation: Physical EOP (!reception_active) while frame_started && !frame_complete -> 3'b111.
 *    - Overrun   : serial_clock strobe while frame_complete && reception_active -> 3'b111.
 * 6. Reset Semantics:
 *    - Active-Low Asynchronous Reset (rst_n == 0).
 */

`default_nettype none

module ares_frame_fsm (
    input  wire       clk,
    input  wire       rst_n,

    // Demodulator & Decoder Stream Inputs
    input  wire       serial_clock,       // Single-cycle sample strobe from Manchester decoder
    input  wire       serial_data,        // Manchester decoded data bit
    input  wire       reception_active,   // Physical packet envelope from Layer-1 Sentinel

    // Layer-2 Fault & Security Outputs
    output reg        frame_fault,        // 1-cycle fault pulse to arbiter
    output reg  [2:0] frame_fault_code,   // Fault classification code
    output reg        frame_complete,     // Asserted when exact 192 bits validated
    output reg  [7:0] bit_counter,        // Autonomous frame bit position (0..192)
    output reg  [1:0] current_state       // Diagnostic FSM state
);

    // FSM State Encoding
    localparam [1:0] STATE_IDLE      = 2'b00;
    localparam [1:0] STATE_RECEIVING = 2'b01;
    localparam [1:0] STATE_COMPLETE  = 2'b10;
    localparam [1:0] STATE_FAULT     = 2'b11;

    // Fault Classification Codes
    localparam [2:0] FAULT_NONE             = 3'b000;
    localparam [2:0] FAULT_PREAMBLE_CORRUPT = 3'b100;
    localparam [2:0] FAULT_TYPE_CORRUPT     = 3'b101;
    localparam [2:0] FAULT_CONSTANT_CORRUPT = 3'b110;
    localparam [2:0] FAULT_TRAILER_CORRUPT  = 3'b111; // Truncation, overrun, boundary error

    // Fixed Protocol Constants
    localparam [15:0] KNOWN_TYPE     = 16'hD391;
    localparam [31:0] KNOWN_CONSTANT = 32'h0DFFFFFE;

    // Frame Tracking Flags
    reg frame_started;
    reg prev_reception_active;

    // Helper wire for expected bit calculation at sample time
    reg expected_bit;
    reg expect_check;
    reg [2:0] check_fault_code;

    always @(*) begin
        expect_check = 1'b0;
        expected_bit = 1'b0;
        check_fault_code = FAULT_NONE;

        if (bit_counter <= 8'd31) begin
            // Preamble: 32'hAAAAAAAA (alternating 1, 0, 1, 0...)
            expect_check = 1'b1;
            expected_bit = (bit_counter[0] == 1'b0) ? 1'b1 : 1'b0;
            check_fault_code = FAULT_PREAMBLE_CORRUPT;
        end else if (bit_counter >= 8'd32 && bit_counter <= 8'd47) begin
            // Type 1: 16'hD391 (MSB first)
            expect_check = 1'b1;
            expected_bit = KNOWN_TYPE[8'd47 - bit_counter];
            check_fault_code = FAULT_TYPE_CORRUPT;
        end else if (bit_counter >= 8'd48 && bit_counter <= 8'd63) begin
            // Type 2: 16'hD391 (MSB first)
            expect_check = 1'b1;
            expected_bit = KNOWN_TYPE[8'd63 - bit_counter];
            check_fault_code = FAULT_TYPE_CORRUPT;
        end else if (bit_counter >= 8'd64 && bit_counter <= 8'd95) begin
            // Constant: 32'h0DFFFFFE (MSB first)
            expect_check = 1'b1;
            expected_bit = KNOWN_CONSTANT[8'd95 - bit_counter];
            check_fault_code = FAULT_CONSTANT_CORRUPT;
        end
        // Bits 96..167 (Payload) and 168..191 (Trailer): expect_check = 0 (unconstrained)
    end

    // Sequential Frame Integrity FSM
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_state         <= STATE_IDLE;
            frame_fault           <= 1'b0;
            frame_fault_code      <= FAULT_NONE;
            frame_complete        <= 1'b0;
            frame_started         <= 1'b0;
            bit_counter           <= 8'd0;
            prev_reception_active <= 1'b0;
        end else begin
            // Single-cycle default strobe
            frame_fault <= 1'b0;
            prev_reception_active <= reception_active;

            case (current_state)

                STATE_IDLE: begin
                    frame_fault_code <= FAULT_NONE;
                    frame_complete   <= 1'b0;
                    bit_counter      <= 8'd0;

                    // Frame starts on first valid serial_clock within an active physical reception envelope
                    if (reception_active && serial_clock) begin
                        frame_started <= 1'b1;
                        if (expect_check && (serial_data != expected_bit)) begin
                            // Preamble bit 0 corrupted immediately
                            frame_fault      <= 1'b1;
                            frame_fault_code <= check_fault_code;
                            current_state    <= STATE_FAULT;
                        end else begin
                            bit_counter   <= 8'd1;
                            current_state <= STATE_RECEIVING;
                        end
                    end
                end

                STATE_RECEIVING: begin
                    // 1. Qualified Truncation Check:
                    // Physical envelope dropped (!reception_active) before completing 192 bits
                    if (prev_reception_active && !reception_active && frame_started && !frame_complete) begin
                        frame_fault      <= 1'b1;
                        frame_fault_code <= FAULT_TRAILER_CORRUPT;
                        current_state    <= STATE_FAULT;
                        frame_started    <= 1'b0;
                        bit_counter      <= 8'd0;
                    end else if (serial_clock) begin
                        // 2. Immediate Field Integrity Verification at sample time
                        if (expect_check && (serial_data != expected_bit)) begin
                            frame_fault      <= 1'b1;
                            frame_fault_code <= check_fault_code;
                            current_state    <= STATE_FAULT;
                        end else begin
                            if (bit_counter == 8'd191) begin
                                // Exact 192nd bit (bit index 191) successfully consumed
                                bit_counter    <= 8'd192;
                                frame_complete <= 1'b1;
                                current_state  <= STATE_COMPLETE;
                            end else begin
                                bit_counter <= bit_counter + 8'd1;
                            end
                        end
                    end
                end

                STATE_COMPLETE: begin
                    // 1. Overrun Check:
                    // If an extra serial_clock strobe arrives after 192 bits while still in active packet envelope
                    if (reception_active && serial_clock) begin
                        frame_fault      <= 1'b1;
                        frame_fault_code <= FAULT_TRAILER_CORRUPT;
                        current_state    <= STATE_FAULT;
                    end else if (!reception_active) begin
                        // Normal End-of-Burst silence: cleanly reset context for next burst
                        current_state  <= STATE_IDLE;
                        frame_complete <= 1'b0;
                        frame_started  <= 1'b0;
                        bit_counter    <= 8'd0;
                    end
                end

                STATE_FAULT: begin
                    // Stay in fault or return to IDLE when physical envelope ends
                    if (!reception_active) begin
                        current_state  <= STATE_IDLE;
                        frame_started  <= 1'b0;
                        frame_complete <= 1'b0;
                        bit_counter    <= 8'd0;
                    end
                end

                default: current_state <= STATE_IDLE;
            endcase
        end
    end

endmodule

`default_nettype wire
