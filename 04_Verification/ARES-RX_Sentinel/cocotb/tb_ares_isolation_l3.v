/*
 * ARES-RX Sentinel: Layer-3 Hardware Fail-Closed Isolation Testbench
 * File: tb_ares_isolation_l3.v
 * Target: Icarus Verilog 13.0 / IEEE 1364-2005
 * Verification Suite: WO-2026-M2-001 (Hardware Fail-Closed Isolation)
 */

`timescale 1us/100ns

module tb_ares_isolation_l3;

    // Simulation Clock: 20 kHz (Period = 50 us, half-period = 25 us)
    reg clk;
    reg rst_n;

    reg        temporal_fault;
    reg  [2:0] fault_code;
    reg  [7:0] raw_data_in;
    reg        raw_valid_in;

    wire [7:0] safe_data_out;
    wire       safe_valid_out;
    wire       fault_latched;
    wire       tamper_alert;
    wire [2:0] latched_fault_code;

    // Instantiate Device Under Test
    ares_isolation_l3 #(
        .DATA_WIDTH(8)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .temporal_fault(temporal_fault),
        .fault_code(fault_code),
        .raw_data_in(raw_data_in),
        .raw_valid_in(raw_valid_in),
        .safe_data_out(safe_data_out),
        .safe_valid_out(safe_valid_out),
        .fault_latched(fault_latched),
        .tamper_alert(tamper_alert),
        .latched_fault_code(latched_fault_code)
    );

    // Clock Generation
    always #25 clk = ~clk;

    integer tests_passed = 0;
    integer total_tests = 5;

    // Task: Reset DUT
    task do_reset;
        begin
            rst_n = 0;
            temporal_fault = 0;
            fault_code = 3'b000;
            raw_data_in = 8'h00;
            raw_valid_in = 0;
            #100;
            @(posedge clk);
            #1;
            rst_n = 1;
            @(posedge clk);
            #1;
        end
    endtask

    initial begin
        $dumpfile("04_Verification/ARES-RX_Sentinel/waveforms/ares_isolation_l3.vcd");
        $dumpvars(0, tb_ares_isolation_l3);

        clk = 0;

        $display("==================================================================");
        $display("ARES-RX Sentinel: Layer-3 Hardware Fail-Closed Isolation Testbench");
        $display("Work Order: WO-2026-M2-001");
        $display("==================================================================");

        // ------------------------------------------------------------
        // TEST 1: Normal Passthrough (fault_latched = 0)
        // ------------------------------------------------------------
        do_reset();
        raw_data_in = 8'hA5;
        raw_valid_in = 1'b1;
        #1;
        if (safe_data_out !== 8'hA5 || safe_valid_out !== 1'b1 || fault_latched !== 1'b0 || tamper_alert !== 1'b0 || latched_fault_code !== 3'b000) begin
            $display("[FAIL] TEST 1: Normal passthrough failed (Expected 8'hA5, got 8'h%02x)", safe_data_out);
            $finish;
        end

        raw_data_in = 8'h5A;
        #1;
        if (safe_data_out !== 8'h5A) begin
            $display("[FAIL] TEST 1: Combinational data tracking failed");
            $finish;
        end
        $display("[PASS] TEST 1: Normal Passthrough (data_out = in_data, tamper_alert = 0)");
        tests_passed = tests_passed + 1;

        // ------------------------------------------------------------
        // TEST 2: Deterministic Zeroization with Zero Additional Clock Latency
        // ------------------------------------------------------------
        // On clock posedge with temporal_fault=1, fault_latched asserts and safe_data_out instantly collapses to 0x00
        raw_data_in = 8'hDE;
        raw_valid_in = 1'b1;
        temporal_fault = 1'b1;
        fault_code = 3'b001; // First fault: RUNT
        @(posedge clk);
        #1; // Output settles immediately on latch clock edge (zero extra cycle latency)
        temporal_fault = 1'b0;

        if (fault_latched !== 1'b1 || safe_data_out !== 8'h00 || safe_valid_out !== 1'b0 || tamper_alert !== 1'b1) begin
            $display("[FAIL] TEST 2: Instant zeroization failed (fault_latched=%b, data_out=0x%02x)", fault_latched, safe_data_out);
            $finish;
        end
        if (latched_fault_code !== 3'b001) begin
            $display("[FAIL] TEST 2: Latched fault code not captured accurately (got %b)", latched_fault_code);
            $finish;
        end
        $display("[PASS] TEST 2: Zero Additional Clock Latency Zeroization (data_out = 0x00, tamper_alert = 1)");
        tests_passed = tests_passed + 1;

        // ------------------------------------------------------------
        // TEST 3: First-Fault Diagnostic Invariant
        // ------------------------------------------------------------
        // Injecting a second, different fault code while already latched MUST NOT overwrite the first fault code
        temporal_fault = 1'b1;
        fault_code = 3'b010; // Second fault: MIDBAND
        @(posedge clk);
        #1;
        temporal_fault = 1'b0;
        fault_code = 3'b011; // Third fault: GAP_RES
        @(posedge clk);
        #1;

        if (latched_fault_code !== 3'b001) begin
            $display("[FAIL] TEST 3: First-fault invariant violated! Latched code was overwritten to %b", latched_fault_code);
            $finish;
        end
        $display("[PASS] TEST 3: First-Fault Invariant (Initial fault code 001 preserved across subsequent faults)");
        tests_passed = tests_passed + 1;

        // ------------------------------------------------------------
        // TEST 4: Sticky Invariant across 1,000 Cycles of Active Input Data
        // ------------------------------------------------------------
        begin : sticky_loop
            integer i;
            for (i = 0; i < 1000; i = i + 1) begin
                raw_data_in = i[7:0];
                raw_valid_in = 1'b1;
                @(posedge clk);
                #1;
                if (fault_latched !== 1'b1 || safe_data_out !== 8'h00 || safe_valid_out !== 1'b0 || tamper_alert !== 1'b1) begin
                    $display("[FAIL] TEST 4: Sticky invariant violated at cycle %0d (data_out=0x%02x)", i, safe_data_out);
                    $finish;
                end
            end
        end
        $display("[PASS] TEST 4: Sticky Isolation Invariant (1,000 cycles with zero leakage)");
        tests_passed = tests_passed + 1;

        // ------------------------------------------------------------
        // TEST 5: Authorized Hardware Reset Recovery
        // ------------------------------------------------------------
        rst_n = 0;
        #100;
        @(posedge clk);
        #1;
        if (fault_latched !== 1'b0 || tamper_alert !== 1'b0 || latched_fault_code !== 3'b000) begin
            $display("[FAIL] TEST 5: Hardware reset did not clear fault state cleanly");
            $finish;
        end

        rst_n = 1;
        raw_data_in = 8'h3C;
        raw_valid_in = 1'b1;
        @(posedge clk);
        #1;
        if (safe_data_out !== 8'h3C || safe_valid_out !== 1'b1 || fault_latched !== 1'b0 || tamper_alert !== 1'b0) begin
            $display("[FAIL] TEST 5: Failed to resume normal passthrough after reset");
            $finish;
        end
        $display("[PASS] TEST 5: Authorized Hardware Reset Recovery (Clean restoration of normal path)");
        tests_passed = tests_passed + 1;

        $display("==================================================================");
        $display("M2 VERILOG SIMULATION SUMMARY: %0d / %0d TESTS PASSED (100%% SUCCESS)", tests_passed, total_tests);
        $display("Waveform saved to: 04_Verification/ARES-RX_Sentinel/waveforms/ares_isolation_l3.vcd");
        $display("==================================================================");
        $finish;
    end

endmodule
