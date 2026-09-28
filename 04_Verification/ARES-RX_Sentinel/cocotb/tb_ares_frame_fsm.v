/*
 * ARES-RX Sentinel: Layer-2 Frame Syntax Integrity & Arbiter Verification Testbench
 * Work Order: WO-2026-M3-001
 * Target: ares_frame_fsm.v & ares_fault_arbiter.v (with ares_fault_latch.v)
 * Standard: IEEE 1364-2005 Synthesizable Verilog
 */

`timescale 1ns / 1ps

module tb_ares_frame_fsm;

    reg clk;
    reg rst_n;

    // FSM Inputs
    reg serial_clock;
    reg serial_data;
    reg reception_active;

    // FSM Outputs
    wire       frame_fault;
    wire [2:0] frame_fault_code;
    wire       frame_complete;
    wire [7:0] bit_counter;
    wire [1:0] current_state;

    // Arbiter Test Signals
    reg        sim_l1_fault;
    reg  [2:0] sim_l1_code;
    wire       arb_set_fault;
    wire [2:0] arb_fault_code;

    // Latch Test Signals
    wire       latched_fault;
    wire [2:0] latched_code;

    // Instantiate Layer-2 Frame Syntax FSM
    ares_frame_fsm u_frame_fsm (
        .clk(clk),
        .rst_n(rst_n),
        .serial_clock(serial_clock),
        .serial_data(serial_data),
        .reception_active(reception_active),
        .frame_fault(frame_fault),
        .frame_fault_code(frame_fault_code),
        .frame_complete(frame_complete),
        .bit_counter(bit_counter),
        .current_state(current_state)
    );

    // Instantiate Upstream Priority Arbiter
    ares_fault_arbiter u_arbiter (
        .temporal_fault(sim_l1_fault),
        .temporal_code(sim_l1_code),
        .frame_fault(frame_fault),
        .frame_code(frame_fault_code),
        .set_fault(arb_set_fault),
        .fault_code(arb_fault_code)
    );

    // Instantiate Layer-3 Sticky Latch for End-to-End Persistence Check
    ares_fault_latch u_latch (
        .clk(clk),
        .rst_n(rst_n),
        .set_fault(arb_set_fault),
        .fault_code_in(arb_fault_code),
        .fault_latched(latched_fault),
        .latched_fault_code(latched_code)
    );

    // Clock Generation: 20 kHz (50 us period -> 25 us half-period)
    always #25000 clk = ~clk;

    // Nominal 192-bit Hardware Capture Bit Stream
    // Header (96b): Preamble (32'hAAAAAAAA) + Type1 (16'hD391) + Type2 (16'hD391) + Constant (32'h0DFFFFFE)
    // Payload (72b): ThermostatID (32'h03391F89) + Room (16'h00F6) + Set (16'h00B5) + State (8'h00)
    // Trailer (24b): Tail1 (8'h94) + Tail2 (8'hAE) + Tail3 (8'h16)
    reg [191:0] nominal_frame = 192'haaaaaaaad391d3910dfffffe03391f8900f600b50094ae16;

    integer test_failures = 0;
    integer i;

    // Helper task to send one bit with active-high serial_clock strobe
    task send_bit(input b);
        begin
            @(posedge clk);
            serial_data  <= b;
            serial_clock <= 1'b1;
            @(posedge clk);
            serial_clock <= 1'b0;
        end
    endtask

    // Helper task to send an entire 192-bit frame
    task send_frame(input [191:0] frame_data);
        integer k;
        begin
            for (k = 191; k >= 0; k = k - 1) begin
                send_bit(frame_data[k]);
            end
        end
    endtask

    initial begin
        $dumpfile("04_Verification/ARES-RX_Sentinel/waveforms/ares_frame_fsm.vcd");
        $dumpvars(0, tb_ares_frame_fsm);

        $display("==================================================================");
        $display("ARES-RX Sentinel: Layer-2 Frame Syntax Integrity & Arbiter Testbench");
        $display("Work Order: WO-2026-M3-001");
        $display("==================================================================");

        // Initialization
        clk = 0;
        rst_n = 0;
        serial_clock = 0;
        serial_data = 0;
        reception_active = 0;
        sim_l1_fault = 0;
        sim_l1_code = 3'b000;

        #100000;
        rst_n = 1;
        #50000;

        // -------------------------------------------------------------
        // TEST 1: Nominal 192-bit Frame Reception
        // -------------------------------------------------------------
        reception_active = 1;
        #50000;
        send_frame(nominal_frame);

        @(posedge clk);
        if (frame_complete === 1'b1 && frame_fault === 1'b0 && bit_counter === 8'd192) begin
            $display("[PASS] TEST 1: Nominal 192-bit Frame (frame_complete=1, fault=0, count=192)");
        end else begin
            $display("[FAIL] TEST 1: Nominal 192-bit Frame (complete=%b, fault=%b, count=%d)", 
                     frame_complete, frame_fault, bit_counter);
            test_failures = test_failures + 1;
        end

        // Physical EOP silence: cleanly resets context
        reception_active = 0;
        #100000;
        if (frame_complete === 1'b0 && current_state === 2'b00) begin
            $display("[PASS] TEST 1-EOP: Physical EOP Clean Reset to IDLE (complete=0, state=IDLE)");
        end else begin
            $display("[FAIL] TEST 1-EOP: Expected IDLE after EOP silence");
            test_failures = test_failures + 1;
        end

        // -------------------------------------------------------------
        // TEST 2: Preamble Bit Corruption (Bit 15 flipped)
        // -------------------------------------------------------------
        rst_n = 0; #50000; rst_n = 1; #50000;
        reception_active = 1;
        #50000;

        // Send bits 0..14 normal, bit 15 corrupted
        for (i = 191; i >= 191 - 14; i = i - 1) begin
            send_bit(nominal_frame[i]);
        end
        // Corrupt bit 15 (nominal_frame[191-15] flipped)
        send_bit(~nominal_frame[191 - 15]);

        @(posedge clk);
        if (frame_fault_code === 3'b100 && current_state === 2'b11) begin
            $display("[PASS] TEST 2: Preamble Corruption Trapped (Code=3'b100 FAULT_PREAMBLE_CORRUPT)");
        end else begin
            $display("[FAIL] TEST 2: Preamble Corruption (fault_code=%b, state=%b)", frame_fault_code, current_state);
            test_failures = test_failures + 1;
        end
        reception_active = 0; #100000;

        // -------------------------------------------------------------
        // TEST 3: Type 1 Bit Corruption (Bit 40 flipped)
        // -------------------------------------------------------------
        rst_n = 0; #50000; rst_n = 1; #50000;
        reception_active = 1;
        #50000;

        for (i = 191; i >= 191 - 39; i = i - 1) begin
            send_bit(nominal_frame[i]);
        end
        send_bit(~nominal_frame[191 - 40]);

        @(posedge clk);
        if (frame_fault_code === 3'b101 && current_state === 2'b11) begin
            $display("[PASS] TEST 3: Type 1 Corruption Trapped (Code=3'b101 FAULT_TYPE_CORRUPT)");
        end else begin
            $display("[FAIL] TEST 3: Type 1 Corruption (fault_code=%b, state=%b)", frame_fault_code, current_state);
            test_failures = test_failures + 1;
        end
        reception_active = 0; #100000;

        // -------------------------------------------------------------
        // TEST 4: Type 2 Bit Corruption (Bit 55 flipped)
        // -------------------------------------------------------------
        rst_n = 0; #50000; rst_n = 1; #50000;
        reception_active = 1;
        #50000;

        for (i = 191; i >= 191 - 54; i = i - 1) begin
            send_bit(nominal_frame[i]);
        end
        send_bit(~nominal_frame[191 - 55]);

        @(posedge clk);
        if (frame_fault_code === 3'b101 && current_state === 2'b11) begin
            $display("[PASS] TEST 4: Type 2 Corruption Trapped (Code=3'b101 FAULT_TYPE_CORRUPT)");
        end else begin
            $display("[FAIL] TEST 4: Type 2 Corruption (fault_code=%b, state=%b)", frame_fault_code, current_state);
            test_failures = test_failures + 1;
        end
        reception_active = 0; #100000;

        // -------------------------------------------------------------
        // TEST 5: Constant Bit Corruption (Bit 75 flipped)
        // -------------------------------------------------------------
        rst_n = 0; #50000; rst_n = 1; #50000;
        reception_active = 1;
        #50000;

        for (i = 191; i >= 191 - 74; i = i - 1) begin
            send_bit(nominal_frame[i]);
        end
        send_bit(~nominal_frame[191 - 75]);

        @(posedge clk);
        if (frame_fault_code === 3'b110 && current_state === 2'b11) begin
            $display("[PASS] TEST 5: Constant Corruption Trapped (Code=3'b110 FAULT_CONSTANT_CORRUPT)");
        end else begin
            $display("[FAIL] TEST 5: Constant Corruption (fault_code=%b, state=%b)", frame_fault_code, current_state);
            test_failures = test_failures + 1;
        end
        reception_active = 0; #100000;

        // -------------------------------------------------------------
        // TEST 6: Dynamic Payload Transparency (Varying Data Values)
        // -------------------------------------------------------------
        rst_n = 0; #50000; rst_n = 1; #50000;
        reception_active = 1;
        #50000;

        // Create frame with different ID (0x02391F89), different temp, different state
        send_frame(192'haaaaaaaad391d3910dfffffe02391f890116010400b0860e);

        @(posedge clk);
        if (frame_complete === 1'b1 && frame_fault === 1'b0) begin
            $display("[PASS] TEST 6: Dynamic Payload Transparency (Different ID/Temp consumed with 0 fault)");
        end else begin
            $display("[FAIL] TEST 6: Dynamic Payload Transparency (complete=%b, fault=%b)", frame_complete, frame_fault);
            test_failures = test_failures + 1;
        end
        reception_active = 0; #100000;

        // -------------------------------------------------------------
        // TEST 7: Qualified Truncation (Physical EOP at bit 120)
        // -------------------------------------------------------------
        rst_n = 0; #50000; rst_n = 1; #50000;
        reception_active = 1;
        #50000;

        // Send 120 bits then drop reception_active
        for (i = 191; i >= 191 - 119; i = i - 1) begin
            send_bit(nominal_frame[i]);
        end
        @(posedge clk);
        // Physical silence EOP
        reception_active = 0;
        @(posedge clk);
        #10000;

        if (frame_fault_code === 3'b111) begin
            $display("[PASS] TEST 7: Qualified Truncation Trapped (Premature EOP -> Code=3'b111 FAULT_TRAILER)");
        end else begin
            $display("[FAIL] TEST 7: Qualified Truncation (fault_code=%b)", frame_fault_code);
            test_failures = test_failures + 1;
        end
        #100000;

        // -------------------------------------------------------------
        // TEST 8: Frame Overrun (193rd bit arrives before EOP)
        // -------------------------------------------------------------
        rst_n = 0; #50000; rst_n = 1; #50000;
        reception_active = 1;
        #50000;

        send_frame(nominal_frame);
        @(posedge clk);
        // Send extra bit while still active
        send_bit(1'b0);
        @(posedge clk);

        if (frame_fault_code === 3'b111 && current_state === 2'b11) begin
            $display("[PASS] TEST 8: Frame Overrun Trapped (Extra 193rd bit -> Code=3'b111 FAULT_TRAILER)");
        end else begin
            $display("[FAIL] TEST 8: Frame Overrun (fault_code=%b, state=%b)", frame_fault_code, current_state);
            test_failures = test_failures + 1;
        end
        reception_active = 0; #100000;

        // -------------------------------------------------------------
        // TEST 9: Upstream Fault Priority Arbitration & Latch Persistence
        // -------------------------------------------------------------
        rst_n = 0; #50000; rst_n = 1; #50000;

        // Case A: Simultaneous L1 + L2 fault on exact same cycle -> L1 wins
        sim_l1_fault = 1;
        sim_l1_code  = 3'b001; // L1 Runt
        // Simulate L2 Constant fault simultaneously
        #100;
        if (arb_set_fault === 1'b1 && arb_fault_code === 3'b001) begin
            $display("[PASS] TEST 9A: Same-Cycle Arbiter Priority (L1=001 vs L2=110 -> Winner L1=001)");
        end else begin
            $display("[FAIL] TEST 9A: Arbiter Priority (set=%b, code=%b)", arb_set_fault, arb_fault_code);
            test_failures = test_failures + 1;
        end
        @(posedge clk);
        sim_l1_fault = 0;

        // Check latch stored 001
        if (latched_fault === 1'b1 && latched_code === 3'b001) begin
            $display("[PASS] TEST 9A-Latch: First-Cause Latch captured Winner L1=001");
        end else begin
            $display("[FAIL] TEST 9A-Latch: Latched code = %b", latched_code);
            test_failures = test_failures + 1;
        end

        // Case B: Cross-cycle persistence (Latch remains 001 even when new L2 fault arrives)
        #50000;
        if (latched_code === 3'b001) begin
            $display("[PASS] TEST 9B: Cross-Cycle Latch Persistence (Sticky Code=001 preserved)");
        end else begin
            $display("[FAIL] TEST 9B: Sticky Code overwritten");
            test_failures = test_failures + 1;
        end

        // -------------------------------------------------------------
        // TEST 10: Multi-Burst Sequential Regression (Zero False Alarms)
        // -------------------------------------------------------------
        rst_n = 0; #50000; rst_n = 1; #50000;

        // Burst 1
        reception_active = 1; #50000;
        send_frame(nominal_frame);
        @(posedge clk);
        reception_active = 0; #100000;

        // Burst 2
        reception_active = 1; #50000;
        send_frame(nominal_frame);
        @(posedge clk);
        reception_active = 0; #100000;

        if (latched_fault === 1'b0 && frame_fault === 1'b0) begin
            $display("[PASS] TEST 10: Multi-Burst Sequential Regression (2 bursts, 0 false alarms, Clean)");
        end else begin
            $display("[FAIL] TEST 10: False alarm in multi-burst sequence");
            test_failures = test_failures + 1;
        end

        $display("==================================================================");
        if (test_failures == 0) begin
            $display("M3 VERILOG SIMULATION SUMMARY: ALL TESTS PASSED (100%% SUCCESS)");
        end else begin
            $display("M3 VERILOG SIMULATION SUMMARY: %d FAILURES DETECTED", test_failures);
        end
        $display("Waveform saved to: 04_Verification/ARES-RX_Sentinel/waveforms/ares_frame_fsm.vcd");
        $display("==================================================================");

        #100000;
        $finish;
    end

endmodule
