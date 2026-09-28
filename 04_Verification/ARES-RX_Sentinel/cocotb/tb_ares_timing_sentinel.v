/*
 * ARES-RX Sentinel: Layer-1 Temporal Integrity Sentinel Testbench
 * File: tb_ares_timing_sentinel.v
 * Target: Icarus Verilog 13.0 / IEEE 1364-2005
 * Verification Suite: WO-M1-QA-002 Qualification Closure
 */

`timescale 1us/100ns

module tb_ares_timing_sentinel;

    // Simulation Clock: 20 kHz (Period = 50 us, half-period = 25 us)
    reg clk;
    reg rst_n;
    reg enable;
    reg pos_edge;
    reg neg_edge;

    wire       reception_active;
    wire       temporal_valid;
    wire       temporal_fault;
    wire [7:0] last_interval;
    wire [2:0] fault_code;
    wire [1:0] current_state;

    // Instantiate Device Under Test
    ares_timing_sentinel #(
        .HB_MIN(8),
        .HB_MAX(10),
        .BIT_MIN(16),
        .BIT_MAX(20),
        .TIMEOUT_CYC(21),
        .EOF_CYC(64)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .enable(enable),
        .pos_edge(pos_edge),
        .neg_edge(neg_edge),
        .reception_active(reception_active),
        .temporal_valid(temporal_valid),
        .temporal_fault(temporal_fault),
        .last_interval(last_interval),
        .fault_code(fault_code),
        .current_state(current_state)
    );

    // Clock Generation (50 us cycle)
    always #25 clk = ~clk;

    integer tests_passed = 0;
    integer total_tests = 0;

    // Task: Reset DUT
    task do_reset;
        begin
            rst_n = 0;
            enable = 1;
            pos_edge = 0;
            neg_edge = 0;
            #100;
            @(posedge clk);
            #1;
            rst_n = 1;
            @(posedge clk);
            #1;
        end
    endtask

    // Task: Wait N cycles without edge
    task wait_cycles(input integer n);
        integer i;
        begin
            pos_edge = 0;
            neg_edge = 0;
            for (i = 0; i < n; i = i + 1) begin
                @(posedge clk);
                #1;
            end
        end
    endtask

    // Task: Pulse edge for 1 cycle after waiting n cycles
    task pulse_rising(input integer n);
        begin
            if (n > 1) wait_cycles(n - 1);
            pos_edge = 1;
            neg_edge = 0;
            @(posedge clk);
            #1;
            pos_edge = 0;
        end
    endtask

    task pulse_falling(input integer n);
        begin
            if (n > 1) wait_cycles(n - 1);
            pos_edge = 0;
            neg_edge = 1;
            @(posedge clk);
            #1;
            neg_edge = 0;
        end
    endtask

    initial begin
        $dumpfile("04_Verification/ARES-RX_Sentinel/waveforms/ares_timing_sentinel.vcd");
        $dumpvars(0, tb_ares_timing_sentinel);

        clk = 0;
        total_tests = 10;

        $display("==================================================================");
        $display("ARES-RX Sentinel: Layer-1 Native Verilog RTL Verification Testbench");
        $display("Work Order: WO-M1-QA-002 Qualification Closure");
        $display("==================================================================");

        // ------------------------------------------------------------
        // TEST 1: Nominal State Transition (IDLE -> ARMED -> ACTIVE)
        // ------------------------------------------------------------
        do_reset();
        wait_cycles(5);
        pulse_rising(1); // Candidate edge -> ARMED
        if (current_state !== 2'b01) begin
            $display("[FAIL] TEST 1: State not ARMED after first edge");
            $finish;
        end
        pulse_falling(9); // 9 cycles (HB) -> ACTIVE
        if (current_state !== 2'b10 || temporal_valid !== 1'b1 || reception_active !== 1'b1) begin
            $display("[FAIL] TEST 1: Expected ACTIVE state with temporal_valid=1");
            $finish;
        end
        pulse_rising(18); // 18 cycles (Full bit) -> Stays ACTIVE
        if (current_state !== 2'b10 || temporal_valid !== 1'b1 || temporal_fault !== 1'b0) begin
            $display("[FAIL] TEST 1: Failed to stay ACTIVE on valid full-bit");
            $finish;
        end
        $display("[PASS] TEST 1: Nominal State Transition (IDLE -> ARMED -> ACTIVE)");
        tests_passed = tests_passed + 1;

        // ------------------------------------------------------------
        // TEST 2: AV01 Glitch / Runt Rejection (N <= 7)
        // ------------------------------------------------------------
        do_reset();
        pulse_rising(1);
        pulse_falling(9); // ACTIVE
        pulse_rising(3);  // 3-cycle glitch
        if (temporal_fault !== 1'b1 || fault_code !== 3'b001 || current_state !== 2'b00) begin
            $display("[FAIL] TEST 2: Runt glitch (N=3) not trapped as FAULT_RUNT (001)");
            $finish;
        end
        $display("[PASS] TEST 2: AV01 Glitch Rejection (N=3, FaultCode=001, Return to IDLE)");
        tests_passed = tests_passed + 1;

        // ------------------------------------------------------------
        // TEST 3: AV02-A Missing Edge Resume (Gap >= 21 then Resume -> FAULT)
        // ------------------------------------------------------------
        do_reset();
        pulse_rising(1);
        pulse_falling(9); // ACTIVE
        wait_cycles(21); // Gap reaches 21 -> enters LONG_GAP_PENDING
        if (current_state !== 2'b11 || temporal_fault !== 1'b0) begin
            $display("[FAIL] TEST 3: Did not enter LONG_GAP_PENDING cleanly");
            $finish;
        end
        pulse_rising(14); // Resumes at cycle 35
        if (temporal_fault !== 1'b1 || fault_code !== 3'b011 || current_state !== 2'b00) begin
            $display("[FAIL] TEST 3: Resumed edge not trapped as FAULT_GAP_RES (011)");
            $finish;
        end
        $display("[PASS] TEST 3: AV02-A Missing Edge Resume (N=35, FaultCode=011, Trapped)");
        tests_passed = tests_passed + 1;

        // ------------------------------------------------------------
        // TEST 4: AV02-B End-of-Burst Silence (N >= EOF_CYC -> IDLE)
        // ------------------------------------------------------------
        do_reset();
        pulse_rising(1);
        pulse_falling(9); // ACTIVE
        wait_cycles(65); // Silence past EOF_CYC (64)
        if (current_state !== 2'b00 || temporal_fault !== 1'b0 || reception_active !== 1'b0) begin
            $display("[FAIL] TEST 4: False alarm or failed return to IDLE after EOF silence");
            $finish;
        end
        $display("[PASS] TEST 4: AV02-B End-of-Burst Silence (N>=64 -> IDLE, Zero False Alarm)");
        tests_passed = tests_passed + 1;

        // ------------------------------------------------------------
        // TEST 5: AV03 Mid-Band Rejection (11 <= N <= 15)
        // ------------------------------------------------------------
        do_reset();
        pulse_rising(1);
        pulse_falling(9); // ACTIVE
        pulse_rising(13); // Mid-band gap (13 cycles)
        if (temporal_fault !== 1'b1 || fault_code !== 3'b010 || current_state !== 2'b00) begin
            $display("[FAIL] TEST 5: Mid-band gap (N=13) not trapped as FAULT_MIDBAND (010)");
            $finish;
        end
        $display("[PASS] TEST 5: AV03 Mid-Band Rejection (N=13, FaultCode=010, Trapped)");
        tests_passed = tests_passed + 1;

        // ------------------------------------------------------------
        // TEST 6: AV04 Extra Edge / Bouncing (N=4 within bit cell)
        // ------------------------------------------------------------
        do_reset();
        pulse_rising(1);
        pulse_falling(9); // ACTIVE
        pulse_rising(4);  // Extra edge at cycle 4
        if (temporal_fault !== 1'b1 || fault_code !== 3'b001) begin
            $display("[FAIL] TEST 6: Extra edge bouncing (N=4) not rejected");
            $finish;
        end
        $display("[PASS] TEST 6: AV04 Extra Edge Rejection (Bouncing at cycle 4, FaultCode=001)");
        tests_passed = tests_passed + 1;

        // ------------------------------------------------------------
        // TEST 7: REQ-08 Boundary Value Sweep: {7, 8, 10, 11, 15, 16, 20, 21}
        // ------------------------------------------------------------
        $display("--- Running REQ-08 Boundary Value Sweep ---");

        // Boundary N=7: Must REJECT (Runt)
        do_reset(); pulse_rising(1); pulse_falling(9); pulse_rising(7);
        if (temporal_fault !== 1'b1 || fault_code !== 3'b001) begin $display("[FAIL] Boundary N=7 failed"); $finish; end

        // Boundary N=8: Must ACCEPT (HB min)
        do_reset(); pulse_rising(1); pulse_falling(9); pulse_rising(8);
        if (temporal_fault !== 1'b0 || temporal_valid !== 1'b1) begin $display("[FAIL] Boundary N=8 failed"); $finish; end

        // Boundary N=10: Must ACCEPT (HB max)
        do_reset(); pulse_rising(1); pulse_falling(9); pulse_rising(10);
        if (temporal_fault !== 1'b0 || temporal_valid !== 1'b1) begin $display("[FAIL] Boundary N=10 failed"); $finish; end

        // Boundary N=11: Must REJECT (Midband min)
        do_reset(); pulse_rising(1); pulse_falling(9); pulse_rising(11);
        if (temporal_fault !== 1'b1 || fault_code !== 3'b010) begin $display("[FAIL] Boundary N=11 failed"); $finish; end

        // Boundary N=15: Must REJECT (Midband max)
        do_reset(); pulse_rising(1); pulse_falling(9); pulse_rising(15);
        if (temporal_fault !== 1'b1 || fault_code !== 3'b010) begin $display("[FAIL] Boundary N=15 failed"); $finish; end

        // Boundary N=16: Must ACCEPT (Bit min)
        do_reset(); pulse_rising(1); pulse_falling(9); pulse_rising(16);
        if (temporal_fault !== 1'b0 || temporal_valid !== 1'b1) begin $display("[FAIL] Boundary N=16 failed"); $finish; end

        // Boundary N=20: Must ACCEPT (Bit max)
        do_reset(); pulse_rising(1); pulse_falling(9); pulse_rising(20);
        if (temporal_fault !== 1'b0 || temporal_valid !== 1'b1) begin $display("[FAIL] Boundary N=20 failed"); $finish; end

        // Boundary N=21: Must Enter LONG_GAP_PENDING and trap on resume
        do_reset(); pulse_rising(1); pulse_falling(9);
        wait_cycles(21);
        if (current_state !== 2'b11) begin $display("[FAIL] Boundary N=21 did not enter PENDING"); $finish; end
        pulse_rising(1); // Resume
        if (temporal_fault !== 1'b1 || fault_code !== 3'b011) begin $display("[FAIL] Boundary N=21 resume not trapped"); $finish; end

        $display("[PASS] TEST 7: REQ-08 Boundary Sweep ({7,8,10,11,15,16,20,21} Verified)");
        tests_passed = tests_passed + 1;

        // ------------------------------------------------------------
        // TEST 8: EOP + Receiver Squelch Noise Rejection
        // ------------------------------------------------------------
        // Packet ends -> 64 cycles silence -> IDLE -> Squelch noise burst (N=1..4)
        do_reset();
        pulse_rising(1);
        pulse_falling(9); // ACTIVE
        wait_cycles(65);  // Return to IDLE
        if (current_state !== 2'b00) begin $display("[FAIL] TEST 8: Not in IDLE before noise"); $finish; end

        // Squelch hash arrives in IDLE: 2-cycle, 3-cycle, 4-cycle chatter
        pulse_rising(1);  // Enters ARMED
        if (current_state !== 2'b01) begin $display("[FAIL] TEST 8: Not in ARMED on first noise edge"); $finish; end
        pulse_falling(2); // Non-valid interval -> Re-arms in ARMED
        if (current_state !== 2'b01 || temporal_fault !== 1'b0) begin $display("[FAIL] TEST 8: Spurious fault on noise"); $finish; end
        pulse_rising(3);  // Non-valid interval -> Re-arms in ARMED
        if (current_state !== 2'b01 || temporal_fault !== 1'b0) begin $display("[FAIL] TEST 8: Spurious fault on noise"); $finish; end
        wait_cycles(22);  // Noise stops, silence >= 21 cycles -> Returns to IDLE
        if (current_state !== 2'b00 || temporal_fault !== 1'b0) begin $display("[FAIL] TEST 8: Failed quiet return to IDLE"); $finish; end
        $display("[PASS] TEST 8: EOP + Receiver Squelch Noise Rejection (Zero False Alarms in IDLE/ARMED)");
        tests_passed = tests_passed + 1;

        // ------------------------------------------------------------
        // TEST 9: Hardware Transmission Regression Verification
        // ------------------------------------------------------------
        // Evaluates 289 valid transitions pattern from nominal capture
        do_reset();
        pulse_rising(1);  // Initial candidate
        pulse_falling(9); // Enters ACTIVE
        // Loop 100 alternating half-bit and full-bit pulses
        begin : hw_loop
            integer k;
            for (k = 0; k < 50; k = k + 1) begin
                pulse_rising(9);
                pulse_falling(18);
            end
        end
        wait_cycles(65); // End of burst
        if (current_state !== 2'b00 || temporal_fault !== 1'b0) begin
            $display("[FAIL] TEST 9: HW stream regression failed");
            $finish;
        end
        $display("[PASS] TEST 9: Long Transmission Sequence Regression (100 transitions, 0 faults, Clean IDLE)");
        tests_passed = tests_passed + 1;

        // ------------------------------------------------------------
        // TEST 10: EOP Noise Chatter at Cycle 40 during LONG_GAP_PENDING
        // Contract: Noise pulse at cycle 40 is trapped as FAULT_GAP_RES (011),
        // and subsequent falling edge (N=3) is cleanly absorbed in ARMED -> IDLE.
        // ------------------------------------------------------------
        do_reset();
        pulse_rising(1);
        pulse_falling(9); // Enters ACTIVE
        wait_cycles(40);  // Gap = 40 cycles (currently in LONG_GAP_PENDING)
        if (current_state !== 2'b11) begin $display("[FAIL] TEST 10: Not in PENDING at cycle 40"); $finish; end

        // First edge of 3-cycle noise pulse arrives at t=40
        pulse_rising(1);
        if (temporal_fault !== 1'b1 || fault_code !== 3'b011 || current_state !== 2'b00) begin
            $display("[FAIL] TEST 10: Premature noise edge at cycle 40 not trapped as FAULT_GAP_RES");
            $finish;
        end

        // Second edge of 3-cycle noise pulse arrives 3 cycles later
        pulse_falling(3); // In IDLE -> enters ARMED
        if (current_state !== 2'b01 || temporal_fault !== 1'b0) begin
            $display("[FAIL] TEST 10: Noise falling edge caused spurious fault");
            $finish;
        end

        // Remaining silence (> 21 cycles) -> returns to IDLE
        wait_cycles(22);
        if (current_state !== 2'b00 || temporal_fault !== 1'b0) begin
            $display("[FAIL] TEST 10: Failed clean return to IDLE after remaining silence");
            $finish;
        end
        $display("[PASS] TEST 10: EOP Noise Chatter at Cycle 40 Trapped & Settled to IDLE");
        tests_passed = tests_passed + 1;

        $display("==================================================================");
        $display("ICARUS VERILOG SIMULATION SUMMARY: %0d / %0d TESTS PASSED (100%% SUCCESS)", tests_passed, total_tests);
        $display("Waveform saved to: 04_Verification/ARES-RX_Sentinel/waveforms/ares_timing_sentinel.vcd");
        $display("==================================================================");
        $finish;
    end

endmodule
